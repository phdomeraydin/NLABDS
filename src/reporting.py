from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class ReportGenerator:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _save_csv(self, rows, filename):
        df = pd.DataFrame(rows)
        df.to_csv(self.output_dir / filename, index=False)
        return df

    def create_all_tables(self, results):
        tables = {}
        tables[2] = self._save_csv([
            {"Configuration": f"P{i}", "Dimension n": r["n"], "Field bit length": r["field_bits"], "Nilpotency class c": 2, "Repetitions": r["repetitions"]}
            for i, r in enumerate(results, start=1)
        ], "Table2_Experimental_Configurations.csv")

        for no, key, name in [(3, "keygen", "Table3_KeyGen.csv"), (4, "sign", "Table4_Sign.csv")]:
            tables[no] = self._save_csv([
                {"n": r["n"], "Mean (ms)": r[key]["mean"], "Median (ms)": r[key]["median"], "SD (ms)": r[key]["sd"], "Min (ms)": r[key]["min"], "Max (ms)": r[key]["max"]}
                for r in results
            ], name)

        tables[5] = self._save_csv([
            {"n": r["n"], "Mean (ms)": r["verify"]["mean"], "Median (ms)": r["verify"]["median"], "SD (ms)": r["verify"]["sd"], "Min (ms)": r["verify"]["min"], "Max (ms)": r["verify"]["max"], "Correctness (%)": r["correctness_rate"]}
            for r in results
        ], "Table5_Verify.csv")

        tables[6] = self._save_csv([
            {"n": r["n"], "Private key (bytes)": r["private_bytes"], "Public key (bytes)": r["public_bytes"], "Signature (bytes)": r["signature_bytes"]}
            for r in results
        ], "Table6_Sizes.csv")

        tables[7] = self._save_csv([
            {"n": r["n"], "Matrix construction mean (ms)": r["matrix_attack"]["mean"], "Linear solve mean (ms)": r["solve_attack"]["mean"], "Total attack mean (ms)": r["attack"]["mean"], "Attack success (%)": r["attack_success_rate"]}
            for r in results
        ], "Table7_Linearization_Attack.csv")

        tables[8] = self._save_csv([
            {"n": r["n"], "Mean rank": r["mean_rank"], "Mean normalized rank rho_g": r["normalized_rank"], "Mean dim C_L(g)": r["mean_nullity"], "Mean normalized centralizer delta_g": r["normalized_nullity"]}
            for r in results
        ], "Table8_Rank_Centralizer.csv")

        tables[9] = self._save_csv([
            {"n": r["n"], "Attack attempts": r["repetitions"], "Compatible secrets recovered": r["compatible_secrets"], "Accepted forged signatures": r["accepted_forgeries"], "Forgery rate (%)": r["forgery_rate"]}
            for r in results
        ], "Table9_Equivalent_Secret_Forgery.csv")

        tables[10] = self._save_csv([
            {"n": r["n"], "T_Legit mean (ms)": r["legit_mean"], "T_Lin mean (ms)": r["attack"]["mean"], "R_T": r["RT"]}
            for r in results
        ], "Table10_Legitimate_vs_Attack.csv")
        return tables

    def create_performance_chart(self, results):
        n_values = [r["n"] for r in results]
        keygen = [r["keygen"]["mean"] for r in results]
        signing = [r["sign"]["mean"] for r in results]
        verification = [r["verify"]["mean"] for r in results]

        x = np.arange(len(n_values))
        width = 0.25
        fig, ax = plt.subplots(figsize=(10, 6))
        bars1 = ax.bar(x - width, keygen, width, label="Key Generation")
        bars2 = ax.bar(x, signing, width, label="Signing")
        bars3 = ax.bar(x + width, verification, width, label="Verification")
        ax.set_xlabel("Lie Algebra Dimension (n)", fontsize=12)
        ax.set_ylabel("Mean Execution Time (ms)", fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(n_values)
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        for bars in (bars1, bars2, bars3):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height:.3f}", xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=9)

        plt.tight_layout()
        fig.savefig(self.output_dir / "KeyGen_Signing_Verification.png", dpi=300, bbox_inches="tight")
        plt.close(fig)

    def create_attack_chart(self, results):
        n_values = [r["n"] for r in results]
        means = [r["attack"]["mean"] for r in results]
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.plot(n_values, means, marker="o")
        ax.set_xlabel("Lie Algebra Dimension (n)")
        ax.set_ylabel("Mean Linearization Attack Time (ms)")
        ax.set_xticks(n_values)
        ax.grid(True, linestyle="--", alpha=0.4)
        plt.tight_layout()
        fig.savefig(self.output_dir / "Linearization_Attack_Time.png", dpi=300, bbox_inches="tight")
        plt.close(fig)

    def create_all_figures(self, results):
        self.create_performance_chart(results)
        self.create_attack_chart(results)
