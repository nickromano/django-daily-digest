# Django Daily Digest

Simple daily summary email with charts.

## Usage

Set a scheduled job to run this once a day.
```
python manage.py send_daily_digest
```

## Contributing

### Local setup

1. Create the virtual environment

```
mkvirtualenv --python=python3 daily-digest
```

2. Install dependencies

```
pip install -r requirements.txt
```

## FAQ

Why isn't python2.7 supported?

> The dependency `CairoSVG` doesn't support anything below python3.4.

Why is the leather project included?

> Upstream `leather` doesn't yet have the ability to show a dashed line. I have a PR for the change in review so in the meantime I am including the fork. The `dependency_links` feature of pip has a deprecation warning and the feature will be removed soon so currently the only option I am aware of is to include the code.
