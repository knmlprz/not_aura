import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image, Imu
from geometry_msgs.msg import Point
from std_msgs.msg import Int32
from visualization_msgs.msg import Marker
from cv_bridge import CvBridge, CvBridgeError
import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R

try:
    from ultralytics import YOLO
except ImportError as exc:
    raise ImportError(
        "Brak pakietu ultralytics. Zainstaluj: pip install ultralytics"
    ) from exc


class PersonTrackerDepthNode(Node):
    """Detekcja ludzi (YOLO COCO person) + odległość z mapy głębi OAK."""

    PERSON_CLASS_ID = 0

    def __init__(self):
        super().__init__('person_tracker_depth_node')

        self.declare_parameter('rgb_topic', '/oak/rgb/image_raw')
        self.declare_parameter('depth_topic', '/oak/stereo/image_raw')
        self.declare_parameter('max_people', 5)
        self.declare_parameter('min_depth_mm', 600.0)
        self.declare_parameter('max_depth_mm', 12000.0)
        self.declare_parameter('model_path', 'yolov8n.pt')
        self.declare_parameter('min_confidence', 0.45)
        self.declare_parameter('iou_threshold', 0.45)
        self.declare_parameter('inference_imgsz', 640)
        self.declare_parameter('viewer_fullscreen', False)
        self.declare_parameter('viewer_width', 0)
        self.declare_parameter('viewer_height', 0)
        self.declare_parameter('imu_topic', '/xreal/imu/data')
        self.declare_parameter('add_block_topic', '/xreal/virtual_scene/add_block')
        self.declare_parameter('person_marker_id_base', 200)
        self.declare_parameter('marker_scale', 0.25)
        self.declare_parameter('marker_height_offset_m', 0.35)
        self.declare_parameter('camera_fx', 0.0)
        self.declare_parameter('camera_fy', 0.0)
        self.declare_parameter('publish_scene_markers', True)

        rgb_topic = str(self.get_parameter('rgb_topic').value)
        depth_topic = str(self.get_parameter('depth_topic').value)
        self.max_people = max(1, int(self.get_parameter('max_people').value))
        self.min_depth_mm = float(self.get_parameter('min_depth_mm').value)
        self.max_depth_mm = float(self.get_parameter('max_depth_mm').value)
        model_path = str(self.get_parameter('model_path').value)
        self.min_confidence = float(self.get_parameter('min_confidence').value)
        self.iou_threshold = float(self.get_parameter('iou_threshold').value)
        self.inference_imgsz = int(self.get_parameter('inference_imgsz').value)
        self.viewer_fullscreen = bool(self.get_parameter('viewer_fullscreen').value)
        self.viewer_width = int(self.get_parameter('viewer_width').value)
        self.viewer_height = int(self.get_parameter('viewer_height').value)
        imu_topic = str(self.get_parameter('imu_topic').value)
        self.add_block_topic = str(self.get_parameter('add_block_topic').value)
        self.person_marker_id_base = int(self.get_parameter('person_marker_id_base').value)
        self.marker_scale = float(self.get_parameter('marker_scale').value)
        self.marker_height_offset_m = float(self.get_parameter('marker_height_offset_m').value)
        self.camera_fx = float(self.get_parameter('camera_fx').value)
        self.camera_fy = float(self.get_parameter('camera_fy').value)
        self.publish_scene_markers = bool(self.get_parameter('publish_scene_markers').value)

        imu_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
        )

        self.show_help_overlay = False
        self.window_name = 'ROS2 Person Tracker (Depth)'
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        if self.viewer_fullscreen:
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

        self.sub_rgb = self.create_subscription(Image, rgb_topic, self.rgb_callback, 10)
        self.sub_depth = self.create_subscription(Image, depth_topic, self.depth_callback, 10)
        self.sub_imu = self.create_subscription(Imu, imu_topic, self.imu_callback, imu_qos)

        self.pub_nearest = self.create_publisher(Point, '/person/nearest', 10)
        self.pub_count = self.create_publisher(Int32, '/person/count', 10)
        self.pub_tracks = [
            self.create_publisher(Point, f'/person/track_{i}', 10)
            for i in range(self.max_people)
        ]
        self.pub_scene_marker = self.create_publisher(Marker, self.add_block_topic, 10)

        self.bridge = CvBridge()
        self.latest_depth_img = None
        self.imu_rot = R.from_quat([0.0, 0.0, 0.0, 1.0])
        self.imu_ready = False

        self.get_logger().info(f'Ladowanie YOLO: {model_path} ...')
        self.model = YOLO(model_path)

        self.SMOOTHING_ALPHA = 0.35
        self.MAX_JUMP_MM = 450.0
        self.MAX_STEP_PER_FRAME_MM = 180.0
        self.DEPTH_QUALITY_MIN = 0.02

        self.prev_z_by_slot = [0.0] * self.max_people

        self.get_logger().info(
            f'Person Tracker: YOLO, depth {self.min_depth_mm:.0f}-{self.max_depth_mm:.0f} mm, '
            f'max_people={self.max_people}, conf>={self.min_confidence:.2f}, '
            f'rgb={rgb_topic}, depth={depth_topic}, imu={imu_topic}, '
            f'scene_markers={self.publish_scene_markers}'
        )

    def imu_callback(self, msg):
        try:
            self.imu_rot = R.from_quat([
                msg.orientation.x,
                msg.orientation.y,
                msg.orientation.z,
                msg.orientation.w,
            ])
            self.imu_ready = True
        except ValueError:
            self.get_logger().warn('Niepoprawny kwaternion IMU.')

    def _camera_basis(self):
        """Osie kamery w ramce xreal_imu (zgodnie z imu_virtual_camera)."""
        forward = self.imu_rot.apply(np.array([0.0, 1.0, 0.0]))
        up = self.imu_rot.apply(np.array([-1.0, 0.0, 0.0]))
        right = np.cross(forward, up)
        right_norm = float(np.linalg.norm(right))
        if right_norm > 1e-9:
            right = right / right_norm
        return forward, up, right

    def pixel_depth_to_imu_position(self, u, v, depth_mm, img_w, img_h):
        """Punkt 3D w xreal_imu z piksela (u,v) i glebokosci [mm]."""
        depth_m = depth_mm / 1000.0
        fx = self.camera_fx if self.camera_fx > 0.0 else img_w * 1.05
        fy = self.camera_fy if self.camera_fy > 0.0 else img_h * 1.05
        cx = img_w * 0.5
        cy = img_h * 0.5

        x_norm = (float(u) - cx) / fx
        y_norm = (float(v) - cy) / fy

        forward, up, right = self._camera_basis()
        return depth_m * forward + depth_m * x_norm * right + depth_m * y_norm * (-up)

    def publish_person_scene_marker(self, slot_idx, detection, depth_mm, img_shape):
        if not self.publish_scene_markers or not self.imu_ready or depth_mm <= 0.0:
            return

        img_h, img_w = img_shape[:2]
        head_u = detection['x'] + detection['w'] // 2
        head_v = detection['y']

        head_pos = self.pixel_depth_to_imu_position(head_u, head_v, depth_mm, img_w, img_h)
        _, up, _ = self._camera_basis()
        marker_pos = head_pos + self.marker_height_offset_m * up

        marker = Marker()
        marker.header.frame_id = 'xreal_imu'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'person_markers'
        marker.id = self.person_marker_id_base + slot_idx
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        marker.pose.position.x = float(marker_pos[0])
        marker.pose.position.y = float(marker_pos[1])
        marker.pose.position.z = float(marker_pos[2])
        marker.pose.orientation.w = 1.0
        marker.scale.x = self.marker_scale
        marker.scale.y = self.marker_scale
        marker.scale.z = self.marker_scale
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.color.a = 1.0
        self.pub_scene_marker.publish(marker)

    def hide_person_scene_marker(self, slot_idx):
        if not self.publish_scene_markers:
            return

        marker = Marker()
        marker.header.frame_id = 'xreal_imu'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'person_markers'
        marker.id = self.person_marker_id_base + slot_idx
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.001
        marker.scale.y = 0.001
        marker.scale.z = 0.001
        marker.color.a = 0.0
        self.pub_scene_marker.publish(marker)

    def depth_callback(self, msg):
        try:
            self.latest_depth_img = self.bridge.imgmsg_to_cv2(msg, '16UC1')
        except CvBridgeError as exc:
            self.get_logger().error(f'Depth error: {exc}')

    @staticmethod
    def _scale_rgb_box_to_depth(x, y, w, h, rgb_shape, depth_shape):
        """Mapuje bbox z RGB na rozdzielczość mapy głębi (OAK często ma inny rozmiar)."""
        rh, rw = rgb_shape[:2]
        dh, dw = depth_shape[:2]
        sx = dw / float(max(rw, 1))
        sy = dh / float(max(rh, 1))
        return (
            int(x * sx),
            int(y * sy),
            max(1, int(w * sx)),
            max(1, int(h * sy)),
        )

    def detect_people(self, bgr_image):
        results = self.model.predict(
            bgr_image,
            classes=[self.PERSON_CLASS_ID],
            conf=self.min_confidence,
            iou=self.iou_threshold,
            imgsz=self.inference_imgsz,
            verbose=False,
        )
        if not results:
            return []

        result = results[0]
        if result.boxes is None or len(result.boxes) == 0:
            return []

        detections = []
        boxes = result.boxes.xyxy.cpu().numpy()
        confs = result.boxes.conf.cpu().numpy()

        for box, conf in zip(boxes, confs):
            x1, y1, x2, y2 = box
            w = max(1, int(x2 - x1))
            h = max(1, int(y2 - y1))
            detections.append({
                'x': int(x1),
                'y': int(y1),
                'w': w,
                'h': h,
                'weight': float(conf),
            })

        detections.sort(key=lambda d: d['weight'], reverse=True)
        detections = detections[: self.max_people]
        detections.sort(key=lambda d: d['x'])
        return detections

    def get_depth_from_bbox(self, bbox, rgb_shape):
        if self.latest_depth_img is None:
            return 0.0, 0.0

        depth = self.latest_depth_img
        bx, by, bw, bh = self._scale_rgb_box_to_depth(
            bbox['x'], bbox['y'], bbox['w'], bbox['h'],
            rgb_shape, depth.shape,
        )

        dh, dw = depth.shape
        x1 = max(0, bx + int(bw * 0.20))
        x2 = min(dw, bx + int(bw * 0.80))
        y1 = max(0, by + int(bh * 0.30))
        y2 = min(dh, by + int(bh * 0.90))
        if x2 <= x1 or y2 <= y1:
            return 0.0, 0.0

        roi = depth[y1:y2, x1:x2]
        if roi.size == 0:
            return 0.0, 0.0

        total_px = int(roi.size)
        valid = roi[(roi > 200) & (roi < int(self.max_depth_mm * 1.15))]
        valid_px = int(valid.size)
        quality = valid_px / total_px if total_px > 0 else 0.0

        if valid_px == 0:
            return 0.0, quality

        return float(np.median(valid)), quality

    def filter_depth(self, raw_z, prev_z, depth_q):
        if raw_z <= 0.0:
            return prev_z if prev_z > 0.0 else 0.0

        raw_z = float(np.clip(raw_z, self.min_depth_mm, self.max_depth_mm))

        if prev_z > 0.0:
            jump = abs(raw_z - prev_z)
            if jump > self.MAX_JUMP_MM:
                step = np.clip(raw_z - prev_z, -self.MAX_JUMP_MM, self.MAX_JUMP_MM)
                raw_z = prev_z + step

        alpha = self.SMOOTHING_ALPHA if depth_q >= self.DEPTH_QUALITY_MIN else self.SMOOTHING_ALPHA * 0.5
        if prev_z <= 0.0:
            filtered = raw_z
        else:
            filtered = alpha * raw_z + (1.0 - alpha) * prev_z

        step = filtered - (prev_z if prev_z > 0.0 else filtered)
        step = np.clip(step, -self.MAX_STEP_PER_FRAME_MM, self.MAX_STEP_PER_FRAME_MM)
        base = prev_z if prev_z > 0.0 else filtered
        return float(np.clip(base + step, self.min_depth_mm, self.max_depth_mm))

    def process_detection(self, detection, slot_idx, rgb_shape):
        cx = detection['x'] + detection['w'] // 2
        cy = detection['y'] + int(detection['h'] * 0.65)
        raw_z, depth_q = self.get_depth_from_bbox(detection, rgb_shape)
        prev_z = self.prev_z_by_slot[slot_idx]
        filtered_z = self.filter_depth(raw_z, prev_z, depth_q)

        if filtered_z > 0.0:
            self.prev_z_by_slot[slot_idx] = filtered_z

        msg = Point()
        msg.x = float(cx)
        msg.y = float(cy)
        msg.z = filtered_z if filtered_z > 0.0 else 0.0
        return {
            'msg': msg,
            'cx': cx,
            'cy': cy,
            'filtered_z': filtered_z,
            'depth_q': depth_q,
            'bbox': detection,
        }

    def draw_detection(self, image, track, slot_idx):
        det = track['bbox']
        x, y, w, h = det['x'], det['y'], det['w'], det['h']
        color = (0, 200, 255)
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.circle(image, (track['cx'], track['cy']), 6, color, -1)

        if track['filtered_z'] > 0.0:
            label = f'P{slot_idx}: {track["filtered_z"] / 1000.0:.2f} m'
        else:
            label = f'P{slot_idx}: brak glebi'

        cv2.putText(image, label, (x, max(20, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
        cv2.putText(
            image,
            f'conf={det["weight"]:.2f} q={track["depth_q"]:.2f}',
            (x, y + h + 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (220, 220, 220),
            1,
            cv2.LINE_AA,
        )

    def rgb_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except CvBridgeError:
            return

        detections = self.detect_people(cv_image)

        tracks = []
        for slot_idx, detection in enumerate(detections):
            tracks.append(self.process_detection(detection, slot_idx, cv_image.shape))

        for slot_idx in range(len(detections), self.max_people):
            self.prev_z_by_slot[slot_idx] = 0.0
            self.pub_tracks[slot_idx].publish(Point())

        nearest_msg = Point()
        nearest_dist = float('inf')
        for slot_idx, track in enumerate(tracks):
            self.pub_tracks[slot_idx].publish(track['msg'])
            self.draw_detection(cv_image, track, slot_idx)
            if track['filtered_z'] > 0.0:
                self.publish_person_scene_marker(
                    slot_idx, track['bbox'], track['filtered_z'], cv_image.shape
                )
            else:
                self.hide_person_scene_marker(slot_idx)
            z = track['filtered_z']
            if z > 0.0 and z < nearest_dist:
                nearest_dist = z
                nearest_msg = track['msg']

        for slot_idx in range(len(tracks), self.max_people):
            self.hide_person_scene_marker(slot_idx)

        count_msg = Int32()
        count_msg.data = len(tracks)
        self.pub_count.publish(count_msg)
        self.pub_nearest.publish(nearest_msg)

        depth_status = 'OK' if self.latest_depth_img is not None else 'brak depth'
        imu_status = 'OK' if self.imu_ready else 'brak IMU'
        cv2.putText(
            cv_image,
            f'YOLO people: {len(tracks)} | depth {depth_status} | IMU {imu_status} | '
            f'{self.min_depth_mm / 1000:.1f}-{self.max_depth_mm / 1000:.1f} m',
            (10, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        display_image = cv_image
        if self.viewer_width > 0 and self.viewer_height > 0:
            display_image = cv2.resize(cv_image, (self.viewer_width, self.viewer_height))

        self._draw_help_hud(display_image)
        cv2.imshow(self.window_name, display_image)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('f'):
            self.viewer_fullscreen = not self.viewer_fullscreen
            prop = cv2.WINDOW_FULLSCREEN if self.viewer_fullscreen else cv2.WINDOW_NORMAL
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, prop)
        elif key == ord('i'):
            self.show_help_overlay = not self.show_help_overlay
        elif key == 27:
            self.viewer_fullscreen = False
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    def _draw_help_hud(self, display_image):
        h_disp, w_disp, _ = display_image.shape
        margin = 10
        icon_width = 28
        icon_height = 28
        x2 = w_disp - margin
        x1 = x2 - icon_width
        y2 = h_disp - margin
        y1 = y2 - icon_height

        overlay = display_image.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (210, 210, 210), thickness=-1, lineType=cv2.LINE_AA)
        cv2.addWeighted(overlay, 0.7, display_image, 0.3, 0, display_image)
        cv2.rectangle(display_image, (x1, y1), (x2, y2), (80, 80, 80), thickness=2, lineType=cv2.LINE_AA)

        font = cv2.FONT_HERSHEY_SIMPLEX
        (text_w, text_h), _ = cv2.getTextSize('i', font, 0.7, 2)
        text_org = (x1 + icon_width // 2 - text_w // 2 + 1, y1 + icon_height // 2 + text_h // 2 - 2)
        cv2.putText(display_image, 'i', text_org, font, 0.7, (60, 60, 60), 2, cv2.LINE_AA)

        if not self.show_help_overlay:
            return

        info_lines = ['F - toggle fullscreen', 'Esc - exit fullscreen', 'i - toggle help']
        scale = 0.5
        thickness = 1
        y = y1
        for line in reversed(info_lines):
            (tw, th), _ = cv2.getTextSize(line, font, scale, thickness)
            text_org = (x1 - margin - tw, y + th)
            cv2.putText(display_image, line, text_org, font, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
            cv2.putText(display_image, line, text_org, font, scale, (255, 255, 255), thickness, cv2.LINE_AA)
            y -= th + 4


def main(args=None):
    rclpy.init(args=args)
    node = PersonTrackerDepthNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
