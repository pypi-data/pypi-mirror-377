<!--suppress HtmlDeprecatedAttribute -->
<div align="center">
  <h1>Federated Learning Manager</h1>
  <img src="docs/docs/img/logo.jpg" width="256" alt="py-fl-manager-logo"/>
</div>

The `py-fl-manager` project provides easy integration with [`NVFlare`](https://github.com/NVIDIA/NVFlare).

> [!WARNING]
> This project is currently in **alpha**.

> [!NOTE]
> The documentation is **in progress**. Some sections may be incomplete, outdated, or missing details.

## Running (example)

> The base docker image used is `fl-manager:dev`, so `make dev/build` should be executed first.

See available examples at [examples](examples). Currently, only `nvflare_mnist` is available.

Access the example folder. There is a `project.yml` with the FL project configuration and a set of folders with jobs examples.

1. Start by provisioning the workspace with `nvflare provision`.
  - For now, (04/02/2025):
    - Copy and paste the job's folders inside `transfer` from the admin folder.
    - Change the `PYTHON_EXECUTABLE` variable inside the `.env`.
    - Change `fed_admin.json` overseer endpoint from 'server1' to 'localhost'.
2. Run `docker compose build` and `docker compose up` to initialize the simulation workspace.
3. Login into the admin CLI (`startup.sh`) script.
4. Submit job!

For (1), the following command can be run to achieve it: `EXAMPLE=nvflare_mnist make dev/provision`.

## Code Quality

This repository provides a configuration for `SonarScanner`. Some missing parameters that should be set before running are the following:

```properties
sonar.projectKey=${PROJECT_KEY}
sonar.projectName=${PROJECT_NAME}
sonar.token=${SONAR_TOKEN}
```

A self-hosted `SonarQube` can be deployed to perform a local analysis.

1. Deploy `SonarQube` with `docker run --name sonarqube-custom -p 9000:9000 sonarqube:community`.
2. Access `SonarQube` and configure a project (default credentials admin:admin).
3. Create a Project and copy the token.
4. Execute tests with coverage using `make dev/test-cov`.
5. Change in `coverage.xml` the `<source>/opt/project/fl_manager</source>` root to `<source>/usr/src/fl_manager</source>`, this enables the coverage support in this local scan.
6. Fill the properties file with the missing values.
7. Run `docker run --rm --network host -e SONAR_HOST_URL="http://localhost:9000" -v $(pwd):/usr/src sonarsource/sonar-scanner-cli`

## Versioning

All packages follow semantic versioning. This means, all versions with the same _major_ must be compatible between them. This way, packages can evolve independently between them. When a _major_ release needs to be done, all packages must be bumped to the new major.

## Contributing

### Creating a new package

1. Execute `make uv_runtime/run`.
2. Create the necessary folders if they do not exist.
3. Run `uv init --no-readme --no-pin-python --lib --name $NAME $PATH`.
4. Mark `src` as source root. Create subfolders for namespace.
5. Add build target (in new package `.toml`) to the namespace package.

### Configuration

We use [`pre-commit`](https://pre-commit.com/) hooks.

#### Setup pre-commit hooks

Probably there will be other methods to install `pre-commit` we use the following steps:

1. Install `pipx` with (system's) `pip` (i.e. `pip install pipx`).
2. Install `pre-commit` with `pipx` (i.e. `pipx install pre-commit`).
3. Follow the instructions that are printed after the execution of the step 2 command, to ensure that `pre-commit` is in the path.
4. Run `pre-commit install`.

Check [`.pre-commit-config.yaml`](.pre-commit-config.yaml) to check what hooks are installed!
