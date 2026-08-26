from .algebra import Class2LieAlgebra, vectors_equal
from .attacks import LinearizationAttack
from .benchmark import BenchmarkRunner
from .config import ExperimentConfig
from .crypto import DigitalSignatureScheme
from .reporting import ReportGenerator


class LieSignatureExperimentApp:
    def __init__(self, config=None):
        self.config = config or ExperimentConfig()
        self.output_dir = self.config.prepare_output_dir()

    def sanity_test(self):
        import random
        rng = random.Random(self.config.master_seed)
        algebra = Class2LieAlgebra.random_algebra(
            n=16,
            p=self.config.prime,
            rng=rng,
            center_fraction=self.config.center_fraction,
            density=self.config.density,
        )
        scheme = DigitalSignatureScheme(algebra, rng)
        k_pub, k_priv = scheme.keygen()
        message = b"Test message"
        sigma = scheme.sign(k_pub, k_priv, message)
        assert scheme.verify(k_pub, message, sigma)

        attack = LinearizationAttack(algebra).run(k_pub)
        assert attack["success"]
        x_prime = attack["x_prime"]
        assert vectors_equal(algebra.phi(x_prime, k_pub["g"]), k_pub["y"])
        forged_message = b"Message never signed by original private key"
        forged_sigma = scheme.sign(k_pub, x_prime, forged_message)
        accepted = scheme.verify(k_pub, forged_message, forged_sigma)
        assert accepted

        print("Sanity test passed.")
        print("Original secret equals recovered secret:", vectors_equal(k_priv, x_prime))
        print("Recovered secret is compatible:", attack["success"])
        print("Forged signature accepted:", accepted)
        print("Rank:", attack["rank"])
        print("Nullity / centralizer dimension:", attack["nullity"])

    def run(self):
        self.sanity_test()
        results = BenchmarkRunner(self.config).run_all()
        reporter = ReportGenerator(self.output_dir)
        tables = reporter.create_all_tables(results)
        reporter.create_all_figures(results)

        for number in sorted(tables):
            print(f"\nTABLE {number}")
            print(tables[number].to_string(index=False))

        print("\nAll CSV and PNG files saved in:", self.output_dir.resolve())
        return results, tables
