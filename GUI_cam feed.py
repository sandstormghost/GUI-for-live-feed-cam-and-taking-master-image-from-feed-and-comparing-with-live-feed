import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget


class WebcamCapture(QMainWindow):
    def __init__(self):
        super().__init__()

        self.master_image = None
        self.status = "No master image captured."

        # Create QLabel widgets to display the live video and master image
        self.live_cam_label = QLabel(self)
        self.master_image_label = QLabel(self)

        # Create QLabel widget to display the status
        self.status_label = QLabel(self.status, self)
        self.status_label.setAlignment(Qt.AlignCenter)

        # Create QVBoxLayout to arrange the labels
        layout = QVBoxLayout()
        layout.addWidget(self.live_cam_label)
        layout.addWidget(self.master_image_label)
        layout.addWidget(self.status_label)

        # Create a central widget to set the layout
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Set the window title and size
        self.setWindowTitle("Webcam Capture")
        self.resize(800, 600)

        # Set up the timer to update the live video
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_live_video)
        self.timer.start(30)

        # Capture master image button
        self.capture_button = QLabel("Press 'C' to capture master image.", self)
        self.capture_button.setAlignment(Qt.AlignCenter)
        self.capture_button.setStyleSheet("font-weight: bold; font-size: 16px; color: red;")
        layout.addWidget(self.capture_button)

    def update_live_video(self):
        # Capture frame from webcam
        ret, frame = self.cap.read()

        if ret:
            # Convert the frame to RGB image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to QImage
            image = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)

            # Resize the image to fit the QLabel widget
            image = image.scaled(self.live_cam_label.width(), self.live_cam_label.height(), Qt.KeepAspectRatio)

            # Set the image to the QLabel widget
            self.live_cam_label.setPixmap(QPixmap.fromImage(image))

            # Compare with the master image
            if self.master_image is not None:
                diff = cv2.absdiff(frame, self.master_image)
                gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)

                # Check if there are any differences
                if cv2.countNonZero(thresh) > 0:
                    self.status = "Status: Difference detected!"
                    self.status_label.setStyleSheet("font-weight: bold; font-size: 16px; background-color: red;")
                else:
                    self.status = "Status: No difference."
                    self.status_label.setStyleSheet("font-weight: bold; font-size: 16px; background-color: green;")

                self.status_label.setText(self.status)

        else:
            self.status = "Status: No webcam detected."
            self.status_label.setStyleSheet("font-weight: bold; font-size: 16px; color: red;")
            self.status_label.setText(self.status)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_C:
            # Capture master image
            ret, frame = self.cap.read()
            if ret:
                self.master_image = frame.copy()
                self.master_image_label.setPixmap(QPixmap.fromImage(
                    QImage(self.master_image.data, self.master_image.shape[1], self.master_image.shape[0],
                           QImage.Format_RGB888).scaled(self.master_image_label.width(),
                                                       self.master_image_label.height(), Qt.KeepAspectRatio)))
                self.capture_button.hide()
                self.status = "Status: Master image captured."
                self.status_label.setStyleSheet("font-weight: bold; font-size: 16px; color: green;")
                self.status_label.setText(self.status)


if __name__ == '__main__':
    app = QApplication([])
    window = WebcamCapture()

    # Open webcam
    window.cap = cv2.VideoCapture(0)

    window.show()
    app.exec_()
