import rospy
from sensor_msgs.msg import Image, PointCloud2
from cv_bridge import CvBridge
import pcl
import cv2

def image_callback(data):
    bridge = CvBridge()
    cv_image = bridge.imgmsg_to_cv2(data, "bgr8")
    cv2.imshow("Drone Camera", cv_image)
    cv2.waitKey(3)

def pointcloud_callback(data):
    pcl_data = pcl.PointCloud()
    pcl.fromROSMsg(data, pcl_data)
    pcl.save(pcl_data, 'pointcloud.pcd')

rospy.init_node('drone_data_listener')
rospy.Subscriber("/drone/camera/image_raw", Image, image_callback)
rospy.Subscriber("/drone/lidar/points", PointCloud2, pointcloud_callback)
rospy.spin()