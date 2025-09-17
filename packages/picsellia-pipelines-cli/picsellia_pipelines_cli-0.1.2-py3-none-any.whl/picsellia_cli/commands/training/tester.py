import typer

from picsellia_cli.commands.training.utils.test import (
    get_training_params,
    normalize_training_io,
    _print_training_io_summary,
)
from picsellia_cli.utils.env_utils import Environment
from picsellia_cli.utils.initializer import init_client
from picsellia_cli.utils.logging import section, kv, bullet, hr
from picsellia_cli.utils.pipeline_config import PipelineConfig
from picsellia_cli.utils.run_manager import RunManager
from picsellia_cli.utils.tester import (
    select_run_dir,
    resolve_run_config_path,
    load_or_init_run_config,
    prepare_auth_and_env,
    save_and_get_run_config_path,
    prepare_python_executable,
    run_pipeline,
)


def test_training(
    pipeline_name: str,
    run_config_file: str | None = None,
    reuse_dir: bool = False,
    organization: str | None = None,
    env: Environment | None = None,
):
    pipeline_config = PipelineConfig(pipeline_name=pipeline_name)
    pipeline_type = pipeline_config.get("metadata", "type")
    run_manager = RunManager(pipeline_dir=pipeline_config.pipeline_dir)

    # ── Run directory ────────────────────────────────────────────────────────
    run_dir = select_run_dir(run_manager=run_manager, reuse_dir=reuse_dir)
    run_config_path = resolve_run_config_path(
        run_manager=run_manager, reuse_dir=reuse_dir, run_config_file=run_config_file
    )

    run_config = load_or_init_run_config(
        run_config_path=run_config_path,
        run_manager=run_manager,
        pipeline_type=pipeline_type,
        pipeline_name=pipeline_name,
        get_params_func=get_training_params,
        default_params=pipeline_config.extract_default_parameters(),
        working_dir=run_dir,
        parameters_name="hyperparameters",
    )

    # ── Environment ─────────────────────────────────────────────────────────
    section("🌍 Environment")
    run_config, env_config = prepare_auth_and_env(
        run_config=run_config, organization=organization, env=env
    )

    kv("Host", env_config["host"])
    kv("Organization", env_config["organization_name"])

    # ── Normalize IO (resolve IDs/URLs) ─────────────────────────────────────
    section("📥 Inputs / 📤 Outputs")
    client = init_client(env_config=env_config)
    try:
        normalize_training_io(client=client, run_config=run_config)
    except typer.Exit as e:
        kv("❌ IO normalization failed", str(e))
        raise

    _print_training_io_summary(run_config)

    # ── Persist run config to run dir ────────────────────────────────────────
    saved_run_config_path = save_and_get_run_config_path(
        run_manager=run_manager, run_dir=run_dir, run_config=run_config
    )

    # ── Virtualenv / Python ─────────────────────────────────────────────────
    section("🐍 Virtual env")
    python_executable = prepare_python_executable(pipeline_config=pipeline_config)

    # ── Build command ────────────────────────────────────────────────────────
    section("▶️ Run")
    run_pipeline(
        pipeline_config=pipeline_config,
        run_config_path=saved_run_config_path,
        python_executable=python_executable,
        api_token=env_config["api_token"],
    )

    # ── Save final config (enriched after run if needed) ─────────────────────
    run_manager.save_run_config(run_dir=run_dir, config_data=run_config)

    section("✅ Done")
    bullet(f"Training pipeline '{pipeline_name}' completed.", accent=True)
    kv("Run dir", run_dir.name)
    hr()
