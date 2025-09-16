# Comtegra GPU Cloud CLI Client

## Basic info

CGC Client is a complete solution to create and manage your compute resources through a CLI interface and Python code. It incorporates CLI and SDK in one package.

CGC CLI is a command line interface for Comtegra GPU Cloud. CGC CLI enables management of your Comtegra GPU Cloud resources. The current version of the app provides support for compute, storage and network resources to be created, listed and deleted. Every compute resource is given to you as a URL, which is accessible from the open Internet.

To enable better access to your storage resources, every account has the ability to spawn a free-of-charge filebrowser which is a local implementation of Dropbox. Remember to mount newly created volumes to it.

For now, we provide the ability to spawn compute resources like:

1. [Jupyter notebook](https://jupyter.org/) with TensorFlow or PyTorch installed as default
2. [Triton inferencing server](https://docs.nvidia.com/deeplearning/triton-inference-server/) for large scale inferencing
3. [Label studio](https://labelstud.io/) for easy management of your data annotation tasks with a variety of modes
4. [Rapids](https://rapids.ai/) suite of accelerated libraries for data processing

Notebooks are equipped with all CUDA libraries and GPU drivers which enable the usage of GPU for accelerated computations.
Apart from compute resources, we provide database engines accessible from within your namespace:

1. [PostgreSQL](https://www.postgresql.org/)
2. [Weaviate](https://weaviate.io/)

More are coming!
Please follow the instructions to get started.

## More info

If you'd like to know more, visit:

- [Comtegra GPU Website](https://cgc.comtegra.cloud)
- [Docs](https://docs.cgc.comtegra.cloud)
