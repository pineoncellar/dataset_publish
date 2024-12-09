import cv2
import os

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

dataset_path = "/home/raspi/dataset/rgbd_dataset_freiburg1_rpy/rgb/"

class CameraNode(Node):
    def __init__(self):
        super().__init__("dataset_camera_node")
        self.publisher_ = self.create_publisher(Image, "camera", 10)
        self.timer = self.create_timer(0.1, self.publish_image)  # 每0.1秒发布一次图像

        # 获取文件夹中的所有图片文件，按文件名排序
        self.image_files = sorted([f for f in os.listdir(dataset_path) if f.endswith('.jpg') or f.endswith('.png')])

        # 检查是否有图片文件
        if len(self.image_files) == 0:
            self.get_logger().error("没有找到任何图片文件")

        self.bridge = CvBridge()

    def publish_image(self):
        # 从列表中弹出一个图片文件名
        image_file = self.image_files.pop(0)  # 从列表头部弹出文件名

        if image_file is None:
            self.get_logger().error(f"图片读取完毕")
            return
        
        # 构造图片的完整路径
        image_path = os.path.join(dataset_path, image_file)
        
        # 读取图片
        img = cv2.imread(image_path)

        if img is None:
            self.get_logger().error(f"无法读取图片: {image_file}")
            return

        # 转换图像为ROS 2消息格式并发布
        image_msg = self.bridge.cv2_to_imgmsg(img, encoding="bgr8")
        self.publisher_.publish(image_msg)
        self.get_logger().info("Published image.")

    def destroy_node(self):
        self.pipeline.stop()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    camera_node = CameraNode()

    try:
        rclpy.spin(camera_node)
    except KeyboardInterrupt:
        camera_node.get_logger().info("Shutting down camera node")
    finally:
        camera_node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()