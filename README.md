# coder

Run Visual Studio Code on any machine, anywhere and access it in the browser.

## Usage

First, deploy the coder charm and the ingress charm:

    juju deploy coder
    juju deploy nginx-ingress-integrator ingress

Then, relate the two in order to get ingress to the coder charm:

    juju add-relation coder ingress

We need to set a password to access the web UI with:

    juju config coder password="foobar"

Optionally, we can set a custom ingress address:

    juju config coder external-hostname="mycode.juju"

If not set, this will default to `coder.juju`.

## Developing

Create and activate a virtualenv with the development requirements:

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

## Building

    charmcraft build

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests
