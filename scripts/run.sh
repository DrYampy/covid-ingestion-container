docker run \
  -v $(pwd):/app \
  -it \
  covid-ingestion-container "$@"