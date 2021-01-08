#!/bin/bash

#COMMAND=$1

#EB_CONFIG_DOCKER_IMAGE_STAGING='aws_beanstalk/staging-app'
#declare -a ENV_VARS=("DATABASE_URL" "DEBUG" "SECRET_KEY")
#JSON=$(/opt/elasticbeanstalk/bin/get-config environment)
#arraylength=${#ENV_VARS[@]}
#EB_CONFIG_DOCKER_ENV_ARGS=()

#for (( i=1; i<${arraylength}+1; i++ ));
#do
#    variable=".${ENV_VARS[$i-1]}"
#    value=$(echo $JSON | jq -r "${variable}")
#    echo ${ENV_VARS[$i-1]}"="${value}>>".env"
#done
# build --env arguments for docker from env var settings
#EB_CONFIG_DOCKER_ENV_ARGS="--env-file .env -d --name=shopblender_pre_deploy "
#sudo docker run ${EB_CONFIG_DOCKER_ENV_ARGS} ${EB_CONFIG_DOCKER_IMAGE_STAGING}

#sudo docker exec shopblender_pre_deploy ${COMMAND}

# clean up
#rm .env
#sudo docker stop shopblender_pre_deploy
#sudo docker rm shopblender_pre_deploy