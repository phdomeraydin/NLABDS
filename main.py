from src import ExperimentConfig, LieSignatureExperimentApp


if __name__ == "__main__":
    config = ExperimentConfig(output_dir="results")
    app = LieSignatureExperimentApp(config)
    app.run()
