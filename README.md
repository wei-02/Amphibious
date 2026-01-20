无人车

1.打开gazebo界面

cd ~/amphibious_description

source devel/setup.bash

roslaunch amphibious_description amphibious.launch

2. 无人车遥控

再开一个终端

cd ~/amphibious_description

source devel/setup.bash

rosrun amphibious_description teleop.py

