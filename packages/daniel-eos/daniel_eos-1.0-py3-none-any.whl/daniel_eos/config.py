import os
# 当前文件夹上层的.evn文件

EOS_APPID=os.getenv("EOS_APPID")
EOS_SECRET=os.getenv("EOS_SECRET")
EOS_BUCKETID=os.getenv("EOS_BUCKETID")
EOS_URL=os.getenv("EOS_URL")
EOS_TOKEN_URL=os.getenv("EOS_TOKEN_URL")
EOS_SAVE_DATA_URL=os.getenv("EOS_SAVE_DATA_URL")
EOS_ONLINE_URL=os.getenv("EOS_ONLINE_URL")
UPLOAD_TEMP_PATH=os.getenv("UPLOAD_TEMP_PATH", '/tmp/upload_temp')
