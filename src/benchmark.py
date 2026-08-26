import random
import statistics
import time

from .algebra import Class2LieAlgebra
from .attacks import LinearizationAttack
from .crypto import DigitalSignatureScheme, serialize_vector


def summarize(values):
    values = list(values)
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def timed_call(func, *args, **kwargs):
    start = time.perf_counter_ns()
    result = func(*args, **kwargs)
    elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
    return result, elapsed_ms


def private_key_size_bytes(algebra):
    return len(serialize_vector([0] * algebra.n, algebra.p))


def public_key_size_bytes(algebra):
    return 2 * private_key_size_bytes(algebra)


def signature_size_bytes(algebra):
    return 2 * private_key_size_bytes(algebra)


class BenchmarkRunner:
    def __init__(self, config):
        self.config = config

    def benchmark_configuration(self, n, seed):
        rng = random.Random(seed)
        algebra = Class2LieAlgebra.random_algebra(
            n=n,
            p=self.config.prime,
            rng=rng,
            center_fraction=self.config.center_fraction,
            density=self.config.density,
        )
        scheme = DigitalSignatureScheme(algebra, rng)
        attack_engine = LinearizationAttack(algebra)

        keygen_times, sign_times, verify_times = [], [], []
        matrix_times, solve_times, attack_times = [], [], []
        ranks, nullities = [], []
        correct_count = attack_success_count = forged_count = compatible_count = 0
        latest_k_pub = latest_k_priv = latest_attack = None

        for rep in range(self.config.repetitions):
            message = f"benchmark-message-{n}-{rep}".encode()
            (k_pub, k_priv), keygen_ms = timed_call(scheme.keygen)
            sigma, sign_ms = timed_call(scheme.sign, k_pub, k_priv, message)
            accepted, verify_ms = timed_call(scheme.verify, k_pub, message, sigma)
            if accepted:
                correct_count += 1

            attack = attack_engine.run(k_pub)
            keygen_times.append(keygen_ms)
            sign_times.append(sign_ms)
            verify_times.append(verify_ms)
            matrix_times.append(attack["matrix_ms"])
            solve_times.append(attack["solve_ms"])
            attack_times.append(attack["total_ms"])
            ranks.append(attack["rank"])
            nullities.append(attack["nullity"])

            if attack["success"]:
                attack_success_count += 1
                compatible_count += 1
                forged_message = f"new-forged-message-{n}-{rep}".encode()
                forged_sigma = scheme.sign(k_pub, attack["x_prime"], forged_message)
                if scheme.verify(k_pub, forged_message, forged_sigma):
                    forged_count += 1

            latest_k_pub, latest_k_priv, latest_attack = k_pub, k_priv, attack

        keygen_stats = summarize(keygen_times)
        sign_stats = summarize(sign_times)
        verify_stats = summarize(verify_times)
        matrix_stats = summarize(matrix_times)
        solve_stats = summarize(solve_times)
        attack_stats = summarize(attack_times)
        mean_rank = statistics.mean(ranks)
        mean_nullity = statistics.mean(nullities)
        legit_mean = keygen_stats["mean"] + sign_stats["mean"] + verify_stats["mean"]

        return {
            "algebra": algebra,
            "n": n,
            "p": self.config.prime,
            "field_bits": self.config.field_bits,
            "repetitions": self.config.repetitions,
            "keygen": keygen_stats,
            "sign": sign_stats,
            "verify": verify_stats,
            "matrix_attack": matrix_stats,
            "solve_attack": solve_stats,
            "attack": attack_stats,
            "correctness_rate": correct_count / self.config.repetitions * 100,
            "attack_success_rate": attack_success_count / self.config.repetitions * 100,
            "forgery_rate": forged_count / compatible_count * 100 if compatible_count else 0.0,
            "compatible_secrets": compatible_count,
            "accepted_forgeries": forged_count,
            "mean_rank": mean_rank,
            "mean_nullity": mean_nullity,
            "normalized_rank": mean_rank / n,
            "normalized_nullity": mean_nullity / n,
            "private_bytes": private_key_size_bytes(algebra),
            "public_bytes": public_key_size_bytes(algebra),
            "signature_bytes": signature_size_bytes(algebra),
            "legit_mean": legit_mean,
            "RT": attack_stats["mean"] / legit_mean if legit_mean > 0 else float("nan"),
            "latest_k_pub": latest_k_pub,
            "latest_k_priv": latest_k_priv,
            "latest_attack": latest_attack,
        }

    def run_all(self):
        results = []
        for index, n in enumerate(self.config.dimensions):
            print(f"Running n={n}, p_bits={self.config.field_bits}, repetitions={self.config.repetitions}")
            results.append(self.benchmark_configuration(n, self.config.master_seed + index))
        return results
