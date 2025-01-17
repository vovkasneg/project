import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QWidget, QFileDialog, QListWidget, QStackedWidget, QSlider
)
from PyQt5.QtGui import QPixmap, QImage, QTransform, QPainter, QColor, QFont
from PyQt5.QtCore import Qt


class ImageGalleryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Галерея с Редактором")
        self.setGeometry(100, 100, 1000, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout(self.central_widget)

        # Список изображений
        self.image_list = QListWidget()
        self.image_list.itemClicked.connect(self.show_image)

        # Просмотр изображения
        self.viewer = QStackedWidget()

        # Метка для отображения изображения
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        #self.viewer.addWidget(self.image_label)

        # Редактор
        self.editor_layout = QVBoxLayout()

        self.editor_layout.addWidget(self.image_label)

        
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setMinimum(-100)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.valueChanged.connect(self.adjust_brightness)
        self.editor_layout.addWidget(QLabel("Яркость"))
        self.editor_layout.addWidget(self.brightness_slider)

        self.filter_bright_button = QPushButton("Фильтр: Яркий")
        self.filter_bright_button.clicked.connect(self.apply_bright_filter)
        self.editor_layout.addWidget(self.filter_bright_button)

        self.filter_bw_button = QPushButton("Фильтр: Черно-Белый")
        self.filter_bw_button.clicked.connect(self.apply_black_white_filter)
        self.editor_layout.addWidget(self.filter_bw_button)

        self.rotate_left_button = QPushButton("Повернуть влево")
        self.rotate_left_button.clicked.connect(self.rotate_left)
        self.editor_layout.addWidget(self.rotate_left_button)

        self.rotate_right_button = QPushButton("Повернуть вправо")
        self.rotate_right_button.clicked.connect(self.rotate_right)
        self.editor_layout.addWidget(self.rotate_right_button)

        self.undo_button = QPushButton("Отменить изменение")
        self.undo_button.clicked.connect(self.undo_change)
        self.editor_layout.addWidget(self.undo_button)

        self.reset_button = QPushButton("Сбросить")
        self.reset_button.clicked.connect(self.reset_image)
        self.editor_layout.addWidget(self.reset_button)

        self.editor_widget = QWidget()
        
        self.editor_widget.setLayout(self.editor_layout)
        self.viewer.addWidget(self.editor_widget)

        # Организация лейаутов
        self.layout.addWidget(self.image_list, 1)
        self.layout.addWidget(self.viewer, 3)

        # Панель инструментов
        self.toolbar = QWidget()
        self.toolbar.show()
        self.toolbar_layout = QVBoxLayout()
        self.toolbar.setLayout(self.toolbar_layout)

        self.add_image_button = QPushButton("Добавить изображение")
        self.add_image_button.clicked.connect(self.add_image)
        self.toolbar_layout.addWidget(self.add_image_button)

        self.save_image_button = QPushButton("Сохранить изображение")
        self.save_image_button.clicked.connect(self.save_image)
        self.toolbar_layout.addWidget(self.save_image_button)

        self.layout.addWidget(self.toolbar, 1)

        self.image_path = None
        self.original_pixmap = None
        self.current_pixmap = None
        self.history = []  # Стек для хранения изменений
    

    def add_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if image_path:
            self.image_list.addItem(image_path)

    def show_image(self, item):
        self.image_path = item.text()
        self.original_pixmap = QPixmap(self.image_path)
        self.current_pixmap = self.original_pixmap
        self.current_pixmap = self.current_pixmap.scaled(200, 200, Qt.KeepAspectRatio)
        self.history.clear()
        self.image_label.setPixmap(self.current_pixmap)
        self.viewer.setCurrentWidget(self.image_label)

    def save_to_history(self):
        if self.current_pixmap:
            self.history.append(self.current_pixmap)

    def adjust_brightness(self, value):
        if self.original_pixmap:
            self.save_to_history()
            image = self.current_pixmap.toImage()
            adjusted_image = QImage(image.size(), QImage.Format_ARGB32)
            for x in range(image.width()):
                for y in range(image.height()):
                    color = image.pixelColor(x, y)
                    adjusted_color = color.lighter(100 + value)
                    adjusted_image.setPixelColor(x, y, adjusted_color)
            self.current_pixmap = QPixmap.fromImage(adjusted_image)
            self.image_label.setPixmap(self.current_pixmap)

    def apply_bright_filter(self):
        if self.current_pixmap:
            self.save_to_history()
            image = self.current_pixmap.toImage()
            bright_image = QImage(image.size(), QImage.Format_ARGB32)
            for x in range(image.width()):
                for y in range(image.height()):
                    color = image.pixelColor(x, y)
                    bright_color = color.lighter(150)
                    bright_image.setPixelColor(x, y, bright_color)
            self.current_pixmap = QPixmap.fromImage(bright_image)
            self.image_label.setPixmap(self.current_pixmap)

    def apply_black_white_filter(self):
        if self.current_pixmap:
            self.save_to_history()
            image = self.current_pixmap.toImage()
            bw_image = QImage(image.size(), QImage.Format_ARGB32)
            for x in range(image.width()):
                for y in range(image.height()):
                    color = image.pixelColor(x, y)
                    gray_value = int(0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue())
                    bw_color = Qt.GlobalColor.white if gray_value > 127 else Qt.GlobalColor.black
                    bw_image.setPixelColor(x, y, bw_color)
            self.current_pixmap = QPixmap.fromImage(bw_image)
            self.image_label.setPixmap(self.current_pixmap)

    def rotate_left(self):
        if self.current_pixmap:
            self.save_to_history()
            transform = QTransform().rotate(-90)
            self.current_pixmap = self.current_pixmap.transformed(transform, Qt.SmoothTransformation)
            self.image_label.setPixmap(self.current_pixmap)

    def rotate_right(self):
        if self.current_pixmap:
            self.save_to_history()
            transform = QTransform().rotate(90)
            self.current_pixmap = self.current_pixmap.transformed(transform, Qt.SmoothTransformation)
            self.image_label.setPixmap(self.current_pixmap)

    def undo_change(self):
        if self.history:
            self.current_pixmap = self.history.pop()
            self.image_label.setPixmap(self.current_pixmap)

    def reset_image(self):
        if self.original_pixmap:
            self.current_pixmap = self.original_pixmap
            self.history.clear()
            self.image_label.setPixmap(self.current_pixmap)

    def save_image(self):
        if self.current_pixmap:
            save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)")
            if save_path:
                self.current_pixmap.save(save_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageGalleryApp()
    window.show()
    window.editor_widget.show()
    sys.exit(app.exec_())