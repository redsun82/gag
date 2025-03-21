import typing

from conftest import expect
from src.ghag.ctx import *


@expect(
    """
# generated from test_workflow.py::test_basic
name: My workflow
on:
  pull_request:
    branches:
    - main
  workflow_dispatch: {}
jobs: {}
"""
)
def test_basic():
    name("My workflow")
    on.pull_request(branches=["main"])
    on.workflow_dispatch()


@expect(
    """
# generated from test_workflow.py::test_name_from_docstring
name: My workflow
on:
  workflow_dispatch: {}
jobs: {}
"""
)
def test_name_from_docstring():
    """My workflow"""
    on.workflow_dispatch()


@expect(
    """
# generated from test_workflow.py::test_pull_request
on:
  pull_request:
    types:
    - opened
    - reopened
    branches:
    - main
    - dev/*
    ignore-branches:
    - dev/ignore
    paths:
    - foo/**
    ignore-paths:
    - foo/bar/**
jobs: {}
"""
)
def test_pull_request():
    on.pull_request(
        types=["opened", "reopened"],
        branches=["main", "dev/*"],
        ignore_branches=["dev/ignore"],
        paths=["foo/**"],
        ignore_paths=["foo/bar/**"],
    )


@expect(
    """
# generated from test_workflow.py::test_merge
on:
  pull_request:
    branches:
    - main
    paths:
    - foo/**
jobs: {}
"""
)
def test_merge():
    on.pull_request(branches=["main"])
    on.pull_request(paths=["foo/**"])


@expect(
    """
# generated from test_workflow.py::test_job
on:
  workflow_dispatch: {}
jobs:
  my_job:
    name: My job
    runs-on: ubuntu-latest
    env:
      FOO: bar
"""
)
def test_job():
    on.workflow_dispatch()

    @job
    def my_job():
        name("My job")
        env(FOO="bar")


@expect(
    """
# generated from test_workflow.py::test_job_name_from_docstring
on:
  workflow_dispatch: {}
jobs:
  my_job:
    name: My job
    runs-on: ubuntu-latest
    env:
      FOO: bar
"""
)
def test_job_name_from_docstring():
    on.workflow_dispatch()

    @job
    def my_job():
        """My job"""
        env(FOO="bar")


@expect(
    """
# generated from test_workflow.py::test_jobs
on:
  workflow_dispatch: {}
jobs:
  job1:
    name: First job
    runs-on: ubuntu-latest
    env:
      FOO: bar
  job2:
    name: Second job
    runs-on: ubuntu-latest
    env:
      BAZ: bazz
"""
)
def test_jobs():
    on.workflow_dispatch()

    @job
    def job1():
        name("First job")
        env(FOO="bar")

    @job
    def job2():
        name("Second job")
        env(BAZ="bazz")


@expect(
    """
# generated from test_workflow.py::test_job_runs_on
on:
  workflow_dispatch: {}
jobs:
  my_job:
    runs-on: windows-latest
"""
)
def test_job_runs_on():
    on.workflow_dispatch()

    @job
    def my_job():
        runs_on("windows-latest")


@expect(
    """
# generated from test_workflow.py::test_strategy_with_cross_matrix
on: {}
jobs:
  a_job:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        x:
        - 1
        - 2
        - 3
        y:
        - a
        - b
        - c
    steps:
    - run: ${{ matrix.x }}, ${{ matrix.y }}
"""
)
def test_strategy_with_cross_matrix():
    @job
    def a_job():
        strategy.matrix(x=[1, 2, 3], y=["a", "b", "c"])
        run(f"{matrix.x}, {matrix.y}")


@expect(
    """
# generated from test_workflow.py::test_strategy_with_include_exclude_matrix
on: {}
jobs:
  a_job:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        include:
        - x: 100
          y: z
          z: 42
        exclude:
        - x: 1
          y: a
        x:
        - 1
        - 2
        - 3
        y:
        - a
        - b
        - c
    steps:
    - run: ${{ matrix.x }}, ${{ matrix.y }}, ${{ matrix.z }}
"""
)
def test_strategy_with_include_exclude_matrix():
    @job
    def a_job():
        strategy.matrix(
            x=[1, 2, 3],
            y=["a", "b", "c"],
            exclude=[{"x": 1, "y": "a"}],
            include=[{"x": 100, "y": "z", "z": 42}],
        )
        run(f"{matrix.x}, {matrix.y}, {matrix.z}")


@expect(
    """
# generated from test_workflow.py::test_strategy_with_fail_fast_and_max_parallel
on: {}
jobs:
  a_job:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        x:
        - 1
        - 2
        - 3
        y:
        - a
        - b
        - c
      fail-fast: true
      max-parallel: 5
    steps:
    - run: ${{ matrix.x }}, ${{ matrix.y }}
"""
)
def test_strategy_with_fail_fast_and_max_parallel():
    @job
    def a_job():
        strategy.matrix(x=[1, 2, 3], y=["a", "b", "c"]).fail_fast().max_parallel(5)
        run(f"{matrix.x}, {matrix.y}")


@expect(
    """
# generated from test_workflow.py::test_strategy_in_workflow
on:
  workflow_dispatch: {}
jobs:
  test_strategy_in_workflow:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        include:
          z: 42
        x:
        - 1
        - 2
        - 3
        y:
        - a
        - b
    steps:
    - run: ${{ matrix.x }}, ${{ matrix.y }}, ${{ matrix.z }}
"""
)
def test_strategy_in_workflow():
    on.workflow_dispatch()
    strategy.matrix(x=[1, 2, 3], y=["a", "b"], include={"z": 42})
    run(f"{matrix.x}, {matrix.y}, {matrix.z}")


@expect(
    """
# generated from test_workflow.py::test_matrix_from_input
on:
  workflow_call:
    inputs:
      i:
        required: true
  workflow_dispatch:
    inputs:
      i:
        required: true
jobs:
  test_matrix_from_input:
    runs-on: ubuntu-latest
    strategy:
      matrix: ${{ fromJson(inputs.i) }}
    steps:
    - run: ${{ matrix.foo }}, ${{ matrix.bar }}
    - name: Fail
      if: contains(inputs.i, 'failed')
"""
)
def test_matrix_from_input(i):
    strategy.matrix(fromJson(i))
    run(f"{matrix.foo}, {matrix.bar}")
    step("Fail").if_(contains(i, "failed"))


@expect(
    """
# generated from test_workflow.py::test_runs_on_in_workflow
on:
  workflow_dispatch: {}
env:
  WORKFLOW_ENV: 1
jobs:
  test_runs_on_in_workflow:
    runs-on: macos-latest
    env:
      JOB_ENV: 2
"""
)
def test_runs_on_in_workflow():
    on.workflow_dispatch()
    env(WORKFLOW_ENV=1)
    runs_on("macos-latest")
    env(JOB_ENV=2)


@expect(
    """
# generated from test_workflow.py::test_runs_on_in_worfklow_with_name
name: Foo bar
on:
  workflow_dispatch: {}
jobs:
  test_runs_on_in_worfklow_with_name:
    name: Foo bar
    runs-on: macos-latest
"""
)
def test_runs_on_in_worfklow_with_name():
    name("Foo bar")
    on.workflow_dispatch()
    runs_on("macos-latest")


@expect(
    """
# generated from test_workflow.py::test_steps
on:
  workflow_dispatch: {}
jobs:
  my_job:
    runs-on: ubuntu-latest
    steps:
    - name: salutations
      run: echo hello
    - run: echo $WHO
      env:
        WHO: world
    - name: catastrophe
      if: failure()
      run: echo oh no
    - name: Checkout
      uses: actions/checkout@v4
      with:
        ref: dev
    - name: My action
      uses: ./my_action
      with:
        arg1: foo
        arg2: bar
    - name: My other action
      uses: ./my_other_action
      with:
        arg1: foo
        arg2: bar
    - continue-on-error: true
      run: one
    - continue-on-error: value
      run: two
"""
)
def test_steps():
    on.workflow_dispatch()

    @job
    def my_job():
        step.run("echo hello").name("salutations")
        run("echo $WHO").env(WHO="world")
        step("catastrophe").run("echo oh no").if_("failure()")
        step.uses("actions/checkout@v4").with_(ref="dev")
        use("./my_action").with_(arg1="foo", arg2="bar")
        use("./my_other_action", arg1="foo", arg2="bar")
        run("one").continue_on_error()
        run("two").continue_on_error("value")


@expect(
    """
# generated from test_workflow.py::test_workflow_dispatch_inputs
on:
  workflow_dispatch:
    inputs:
      foo:
        description: a foo
        required: true
        type: string
      bar:
        description: a bar
        required: false
        type: boolean
      baz:
        required: false
        default: b
        type: choice
        options:
        - a
        - b
        - c
      an_env:
        required: false
        type: environment
jobs: {}
"""
)
def test_workflow_dispatch_inputs():
    on.workflow_dispatch.input("foo", description="a foo", required=True).input(
        "bar", "a bar", type="boolean"
    )
    on.workflow_dispatch.input(
        "baz", type="choice", options=["a", "b", "c"], default="b"
    )
    on.workflow_dispatch.input("an_env", type="environment")


@expect(
    """
# generated from test_workflow.py::test_workflow_call
on:
  workflow_call:
    inputs:
      foo:
        required: true
        type: string
      bar:
        required: false
        type: boolean
      baz:
        required: false
        default: b
        type: choice
        options:
        - a
        - b
        - c
    secrets:
      token:
        required: true
      auth:
        description: auth if provided
        required: false
jobs: {}
"""
)
def test_workflow_call():
    (
        on.workflow_call.input("foo", required=True)
        .input("bar", type="boolean")
        .input("baz", type="choice", options=["a", "b", "c"], default="b")
        .secret("token", required=True)
        .secret("auth", "auth if provided")
    )


@expect(
    """
# generated from test_workflow.py::test_inputs
on:
  workflow_call:
    inputs:
      foo:
        description: a foo
        required: true
        type: string
      bar:
        required: false
        default: 42
        type: number
  workflow_dispatch:
    inputs:
      foo:
        description: a foo
        required: true
        type: string
      bar:
        required: false
        default: 42
        type: number
jobs: {}
"""
)
def test_inputs():
    input("foo", description="a foo", required=True)
    input("bar", type="number", default=42)


@expect(
    """
# generated from test_workflow.py::test_trigger_removal
on:
  workflow_call:
    inputs:
      foo:
        description: a foo
        required: false
        type: string
jobs: {}
"""
)
def test_trigger_removal():
    input("foo", "a foo")
    on.workflow_dispatch(None)


@expect(
    """
# generated from test_workflow.py::test_use_input_as_expr
on:
  workflow_call:
    inputs:
      foo:
        description: a foo
        required: false
        type: string
  workflow_dispatch:
    inputs:
      foo:
        description: a foo
        required: false
        type: string
jobs:
  test_use_input_as_expr:
    runs-on: ubuntu-latest
    steps:
    - run: foo is ${{ inputs.foo }}
"""
)
def test_use_input_as_expr():
    foo = input("foo", "a foo")
    run(f"foo is {foo}")


@expect(
    """
# generated from test_workflow.py::test_inputs_from_parameters
on:
  workflow_call:
    inputs:
      foo:
        description: a foo
        required: true
        type: number
      bar:
        required: true
        type: choice
        options:
        - apple
        - orange
        - banana
      c:
        required: true
        type: choice
        options:
        - one
        - two
      baz:
        required: false
        default: 42
        type: number
  workflow_dispatch:
    inputs:
      foo:
        description: a foo
        required: true
        type: number
      bar:
        required: true
        type: choice
        options:
        - apple
        - orange
        - banana
      c:
        required: true
        type: choice
        options:
        - one
        - two
      baz:
        required: false
        default: 42
        type: number
jobs:
  test_inputs_from_parameters:
    runs-on: ubuntu-latest
    steps:
    - run: foo is ${{ inputs.foo }}
"""
)
def test_inputs_from_parameters(foo: int, bar, c: typing.Literal["one", "two"], baz=42):
    foo.description = "a foo"
    bar.type = "choice"
    bar.options = ["apple", "orange", "banana"]
    run(f"foo is {foo}")


@expect(
    """
# generated from test_workflow.py::test_id
on: {}
jobs:
  test_id:
    runs-on: ubuntu-latest
    steps:
    - id: one
      run: one
    - id: y-1
      run: two
    - id: yy
      run: two prime
    - id: y
      run: three
    - name: use x
      run: ${{ steps.one.outputs }}
    - name: use y
      run: ${{ steps.y-1.outcome }}
    - name: use yy
      run: ${{ steps.yy.outputs.a }}
    - name: use z
      run: ${{ steps.y.result }}
    - id: step-1
      name: anon0
    - id: step-2
      name: anon1
    - id: step-3
      name: anon2
    - name: use anonymous
      run: |
        ${{ steps.step-1.outcome }}
        ${{ steps.step-2.outcome }}
        ${{ steps.step-3.outcome }}
"""
)
def test_id():
    x = step.id("one").run("one")
    y = step.run("two")
    yy = step.run("two prime").returns("a")
    z = step.id("y").run("three")

    step("use x").run(x.outputs)
    step("use y").run(y.outcome)
    step("use yy").run(yy.outputs.a)
    step("use z").run(z.result)

    code = "\n".join(str(step(f"anon{i}").outcome) for i in range(3))
    step("use anonymous").run(code)


@expect(
    """
# generated from test_workflow.py::test_steps_array
on: {}
jobs:
  j:
    runs-on: ubuntu-latest
    steps:
    - name: ${{ steps.*.result }}
"""
)
def test_steps_array():
    @job
    def j():
        step(steps._.result)


@expect(
    """
# generated from test_workflow.py::test_if_expr
on: {}
jobs:
  test_if_expr:
    runs-on: ubuntu-latest
    steps:
    - id: x
      run: one
    - if: steps.x.outcome == 'success'
      run: two
    - if: '!steps.x.outputs'
      run: three
"""
)
def test_if_expr():
    x = step.run("one")
    step.run("two").if_(x.outcome == "success")
    step.run("three").if_(~x.outputs)


@expect(
    """
# generated from test_workflow.py::test_implicit_job_outputs
on: {}
jobs:
  j1:
    runs-on: ubuntu-latest
    outputs:
      one: ${{ steps.x.outputs.one }}
      two: ${{ steps.x.outputs.two }}
    steps:
    - id: x
      name: x
      run: |
        echo one=a >> $GITHUB_OUTPUTS
        echo two=b >> $GITHUB_OUTPUTS
  j2:
    runs-on: ubuntu-latest
    outputs:
      one: ${{ steps.x.outputs.one }}
      two: ${{ steps.x.outputs.two }}
      three: ${{ steps.y.outputs.three }}
      a: ${{ matrix.a }}
    strategy:
      matrix:
        a:
        - 1
        - 2
        - 3
    steps:
    - id: x
      name: x
      run: |
        echo one=a >> $GITHUB_OUTPUTS
        echo two=b >> $GITHUB_OUTPUTS
    - id: y
      name: y
      run: echo three=c >> $GITHUB_OUTPUTS
  j3:
    runs-on: ubuntu-latest
    outputs:
      one: ${{ steps.step-2.outputs.one }}
      two: ${{ steps.step-1.outputs.two }}
      a: ${{ matrix.a }}
    strategy:
      matrix:
        a:
        - 1
        - 2
        - 3
    steps:
    - id: step-1
      run: |
        echo one=a >> $GITHUB_OUTPUTS
        echo two=b >> $GITHUB_OUTPUTS
    - id: step-2
      run: echo one=c >> $GITHUB_OUTPUTS
"""
)
def test_implicit_job_outputs():
    @job
    def j1():
        x = step("x").returns(one="a", two="b")
        outputs(x)

    @job
    def j2():
        strategy.matrix(a=[1, 2, 3])
        x = step("x").returns(one="a", two="b")
        y = step("y").returns(three="c")
        outputs(x, y, matrix.a)

    @job
    def j3():
        strategy.matrix(a=[1, 2, 3])
        step.returns(one="a", two="b")
        step.returns(one="c")
        outputs("*", matrix.a)


@expect(
    """
# generated from test_workflow.py::test_explicit_job_outputs
on: {}
jobs:
  j:
    runs-on: ubuntu-latest
    outputs:
      foo: ${{ steps.x.outputs.one }}
      bar: ${{ steps.y.outputs.three }}
      baz: ${{ matrix.a }}
    strategy:
      matrix:
        a:
        - 1
        - 2
        - 3
    steps:
    - id: x
      name: x
      run: |
        echo one=a >> $GITHUB_OUTPUTS
        echo two=b >> $GITHUB_OUTPUTS
    - id: y
      name: y
      run: echo three=c >> $GITHUB_OUTPUTS
"""
)
def test_explicit_job_outputs():
    @job
    def j():
        strategy.matrix(a=[1, 2, 3])
        x = step("x").returns(one="a", two="b")
        y = step("y").returns(three="c")
        outputs(foo=x.outputs.one, bar=y.outputs.three, baz=matrix.a)


@expect(
    """
# generated from test_workflow.py::test_implicit_workflow_outputs
on: {}
outputs:
  one: ${{ jobs.j1.outputs.one }}
  two: ${{ jobs.j1.outputs.two }}
jobs:
  j1:
    runs-on: ubuntu-latest
    outputs:
      one: 1
      two: 2
  j2:
    runs-on: ubuntu-latest
    outputs:
      three: 3
"""
)
def test_implicit_workflow_outputs():
    @job
    def j1():
        outputs(one=1, two=2)

    @job
    def j2():
        outputs(three=3)

    outputs(j1)


@expect(
    """
# generated from test_workflow.py::test_jolly_workflow_outputs
on: {}
outputs:
  one: ${{ jobs.j1.outputs.one }}
  two: ${{ jobs.j1.outputs.two }}
  three: ${{ jobs.j2.outputs.three }}
jobs:
  j1:
    runs-on: ubuntu-latest
    outputs:
      one: 1
      two: 2
  j2:
    runs-on: ubuntu-latest
    outputs:
      three: 3
"""
)
def test_jolly_workflow_outputs():
    @job
    def j1():
        outputs(one=1, two=2)

    @job
    def j2():
        outputs(three=3)

    outputs("*")


@expect(
    """
# generated from test_workflow.py::test_needs
on: {}
jobs:
  j1:
    runs-on: ubuntu-latest
  j2:
    needs:
    - j1
    runs-on: ubuntu-latest
    steps:
    - run: ${{ needs.j1 }}
  j3:
    needs:
    - j1
    - j2
    runs-on: ubuntu-latest
    steps:
    - run: ${{ needs.j1 }}
    - run: ${{ needs.j2 }}
"""
)
def test_needs():
    @job
    def j1():
        pass

    @job
    def j2():
        needs(j1)
        run(j1)

    @job
    def j3():
        needs(j1, j2)
        run(j1)
        run(j2)


@expect(
    """
# generated from test_workflow.py::test_job_as_context
on: {}
jobs:
  test_job_as_context:
    runs-on: ubuntu-latest
    steps:
    - run: 'false'
    - if: always()
      run: echo ${{ job.status }}
"""
)
def test_job_as_context():
    run("false")
    run(f"echo {job.status}").if_(always())


@expect(
    """
# generated from test_workflow.py::test_container
on: {}
jobs:
  j1:
    runs-on: ubuntu-latest
    container:
      image: node:18
      env:
        NODE_ENV: development
      ports:
      - 80
      volumes:
      - my_docker_volume:/volume_mount
      options:
      - --cpus 1
    steps:
    - run: echo ${{ job.container.id }}
  j2:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/owner/image
      credentials:
        username: foo
        password: baz
"""
)
def test_container():
    @job
    def j1():
        container("node:18").env(NODE_ENV="development").ports([80])
        container.volumes(["my_docker_volume:/volume_mount"]).options(["--cpus 1"])
        run(f"echo {job.container.id}")

    @job
    def j2():
        container.image("ghcr.io/owner/image").credentials(
            username="foo", password="baz"
        )


@expect(
    """
# generated from test_workflow.py::test_services
on: {}
jobs:
  test_services:
    runs-on: ubuntu-latest
    services:
      nginx:
        image: nginx:latest
        ports:
        - 8080:80
      redis:
        ports:
        - 6379/tcp
    steps:
    - run: echo ${{ job.services.nginx.id }}
    - run: echo ${{ job.services.redis.ports[6379] }}
"""
)
def test_services():
    service("nginx", image="nginx:latest", ports=["8080:80"])
    service("redis", ports=["6379/tcp"])
    run(f"echo {job.services.nginx.id}")
    run(f"echo {job.services.redis.ports[6379]}")
