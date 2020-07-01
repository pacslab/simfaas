IMAGE_NAME=nimamahmoudi/pacssim-api
docker build -t $IMAGE_NAME:latest -f Dockerfile .
docker run -it --rm -p 5000:5000 --name pacssimapi $IMAGE_NAME
