from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="technobits-auth-django",
    version="1.0.0",
    author="Technobits",
    author_email="dev@technobits.com",
    description="Technobits Authentication Django Package - Complete authentication system with Google OAuth, reCAPTCHA, and SendInBlue email integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/technobits/technobits-library",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=4.0,<6.0",
        "djangorestframework>=3.14.0",
        "djangorestframework-simplejwt>=5.3.0",
        "django-cors-headers>=4.3.0",
        "google-auth>=2.23.0",
        "requests>=2.31.0",
        "sib-api-v3-sdk>=7.6.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-django>=4.5",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "redis": ["redis>=4.0"],
        "postgres": ["psycopg2-binary>=2.9"],
        "production": [
            "redis>=4.0",
            "psycopg2-binary>=2.9",
            "gunicorn>=21.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

