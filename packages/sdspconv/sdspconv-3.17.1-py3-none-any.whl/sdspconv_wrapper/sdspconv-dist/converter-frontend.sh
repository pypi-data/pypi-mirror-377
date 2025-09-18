#!/bin/bash -f

# Auto-generated file: this file originated in template file "template-script.sh" and changed in Pack.kt by sa
if [ -z $ENV_DIR ]; then
  BASEPATH=$(readlink -f "$0")
  export ENV_DIR="$(dirname "${BASEPATH}")"
fi
JIB_MC=`cat $ENV_DIR/converter-frontend/jib-main-class-file`

# Check if the directory '$ENV_DIR/libs' exists
#if [ -d "$ENV_DIR/libs" ]; then
    # Directory exists; Adjusting classpath including specific adjustments for libs
    CP=$(cat "$ENV_DIR/converter-frontend/jib-classpath-file" | \
         sed -e 's,:,\n,g' | \
         sed "s,^,$ENV_DIR/,g" | \
         sed "s,converter-frontend/libs,libs,g" | \
         tr "\n" :)
#else
#    # Directory does not exist; Adjusting classpath without specific adjustments for libs
#    CP=$(cat "$ENV_DIR/converter-frontend/jib-classpath-file" | \
#         sed -e 's,:,\n,g' | \
#         sed "s,^,$ENV_DIR/,g" | \
#         tr "\n" :)
#fi

java -Xss32m $JVM_PARAMS -cp $CP $JIB_MC "$@"
