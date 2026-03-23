import os
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image, ImageTk

from rmbg import remove_background_from_file

ctk.set_appearance_mode("dark")


# Material Design 3 Colors
MD3_PRIMARY = "#6750A4"
MD3_ON_PRIMARY = "#FFFFFF"
MD3_PRIMARY_CONTAINER = "#EADDFF"
MD3_ON_PRIMARY_CONTAINER = "#21005D"
MD3_SECONDARY = "#625B71"
MD3_SECONDARY_CONTAINER = "#E8DEF8"
MD3_TERTIARY = "#7D5260"
MD3_ERROR = "#B3261E"
MD3_ERROR_CONTAINER = "#F9DEDC"
MD3_BACKGROUND = "#1C1B1F"
MD3_ON_BACKGROUND = "#E6E1E5"
MD3_SURFACE = "#2B2930"
MD3_SURFACE_VARIANT = "#49454F"
MD3_ON_SURFACE = "#E6E1E5"
MD3_ON_SURFACE_VARIANT = "#CAC4D0"
MD3_OUTLINE = "#938F99"
MD3_OUTLINE_VARIANT = "#49454F"


class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RMBG2")
        self.root.geometry("1000x600")
        self.root.resizable(False, False)
        self.root.configure(fg_color=MD3_BACKGROUND)

        self.selected_image_path = None
        self.processed_image_path = None  # 保存处理后的图片路径
        self.left_photo = None
        self.right_photo = None

        self.setup_ui()

    def setup_ui(self):
        padding = 24

        # 主容器
        main_frame = ctk.CTkFrame(self.root, fg_color=MD3_BACKGROUND)
        main_frame.pack(fill="both", expand=True, padx=padding, pady=padding)

        # 左侧图片区域
        left_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=28,
            fg_color=MD3_SURFACE,
            border_color=MD3_OUTLINE_VARIANT,
            border_width=1,
        )
        left_frame.pack(side="left", padx=padding / 2, fill="both", expand=True)

        self.left_frame = left_frame  # 保存引用用于动态计算
        self.left_image_label = ctk.CTkLabel(left_frame, text="")
        self.left_image_label.place(relx=0.5, rely=0.43, anchor="center")

        self.left_placeholder = ctk.CTkLabel(
            left_frame,
            text="选择图片",
            font=ctk.CTkFont(size=20, weight="normal"),
            text_color=MD3_ON_SURFACE_VARIANT,
        )
        self.left_placeholder.place(relx=0.5, rely=0.43, anchor="center")

        self.delete_btn = ctk.CTkButton(
            left_frame,
            text="移除",
            command=self.clear_image,
            width=100,
            height=40,
            corner_radius=20,
            fg_color=MD3_SURFACE_VARIANT,
            hover_color=MD3_OUTLINE,
            text_color=MD3_ON_SURFACE,
            font=ctk.CTkFont(size=14, weight="normal"),
        )
        self.delete_btn.place(relx=0.5, rely=0.88, anchor="center")
        self.delete_btn.lower()

        for widget in [self.left_image_label, self.left_placeholder]:
            widget.bind("<Button-1>", lambda e: self.select_image())
        left_frame.bind("<Button-1>", lambda e: self.select_image())

        # 中间执行按钮
        self.process_btn = ctk.CTkButton(
            main_frame,
            text="执行抠图",
            command=self.process_image,
            width=130,
            height=56,
            corner_radius=28,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#7C5DF0",
            hover_color="#6B4ED9",
            text_color="#FFFFFF",
        )
        self.process_btn.pack(side="left", padx=padding / 2)
        self.process_btn.configure(state="disabled")

        # 右侧结果区域
        right_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=28,
            fg_color=MD3_SURFACE,
            border_color=MD3_OUTLINE_VARIANT,
            border_width=1,
        )
        right_frame.pack(side="left", padx=padding / 2, fill="both", expand=True)

        self.right_frame = right_frame  # 保存引用用于动态计算
        self.right_image_label = ctk.CTkLabel(right_frame, text="")
        self.right_image_label.place(relx=0.5, rely=0.43, anchor="center")

        self.save_btn = ctk.CTkButton(
            right_frame,
            text="保存图片",
            command=self.save_image,
            width=120,
            height=40,
            corner_radius=20,
            fg_color="#7C5DF0",
            hover_color="#6B4ED9",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="normal"),
        )
        self.save_btn.place(relx=0.5, rely=0.88, anchor="center")
        self.save_btn.lower()

        self.right_placeholder = ctk.CTkLabel(
            right_frame,
            text="处理结果",
            font=ctk.CTkFont(size=20, weight="normal"),
            text_color=MD3_ON_SURFACE_VARIANT,
        )
        self.right_placeholder.place(relx=0.5, rely=0.43, anchor="center")

    def select_image(self):
        # 已有图片时不重复添加
        if self.selected_image_path:
            return
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("所有文件", "*"),
            ],
        )

        if file_path:
            self.selected_image_path = file_path
            self.display_left_image(file_path)
            self.left_placeholder.lower()
            self.left_image_label.lift()
            self.delete_btn.lift()
            self.process_btn.configure(state="normal")

    def _get_container_size(self, frame):
        """获取容器可用大小（减去padding和按钮空间）"""
        frame.update_idletasks()
        w = frame.winfo_width()
        h = frame.winfo_height()
        # 减去按钮高度和padding
        return max(w - 40, 100), max(h - 140, 100)

    def display_left_image(self, path):
        try:
            img = Image.open(path)
            self.left_photo = img  # 保存原图引用
            self._resize_left_image()
        except Exception as e:
            self.left_placeholder.configure(text="加载失败")
            self.left_placeholder.lift()

    def _resize_left_image(self):
        """根据容器大小调整图片显示"""
        self.left_frame.update_idletasks()
        w = self.left_frame.winfo_width()
        h = self.left_frame.winfo_height()
        size = (max(w - 40, 100), max(h - 140, 100))
        img = self.left_photo.copy()
        img.thumbnail(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        self.left_photo_display = photo  # 保持引用
        self.left_image_label.configure(image=photo)

    def clear_image(self):
        self.selected_image_path = None
        self.left_photo = None
        self.left_image_label.configure(image="")
        self.left_placeholder.lift()
        self.left_image_label.lower()
        self.delete_btn.lower()
        self.process_btn.configure(state="disabled")

    def _set_buttons_state(self, state):
        """统一设置所有按钮状态"""
        self.delete_btn.configure(state=state)
        self.process_btn.configure(state=state)

    def _do_process(self):
        """实际处理图片"""
        if self.selected_image_path:
            try:
                # 使用 RMBG 移除背景
                result_img = remove_background_from_file(self.selected_image_path)

                # 保存处理后的图片到临时文件
                import tempfile

                temp_dir = tempfile.gettempdir()
                original_name = os.path.splitext(
                    os.path.basename(self.selected_image_path)
                )[0]
                self.processed_image_path = os.path.join(
                    temp_dir, f"{original_name}_rmbg.png"
                )
                result_img.save(self.processed_image_path, format="PNG")
                self.right_photo = result_img  # 保存处理后图片引用
                self._resize_right_image()
            except Exception as e:
                self.right_placeholder.configure(text=f"处理失败: {str(e)}")
                self.right_placeholder.lift()

    def _resize_right_image(self):
        """根据容器大小调整图片显示"""
        self.right_frame.update_idletasks()
        w = self.right_frame.winfo_width()
        h = self.right_frame.winfo_height()
        size = (max(w - 40, 100), max(h - 140, 100))
        img = self.right_photo.copy()
        img.thumbnail(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        self.right_photo_display = photo  # 保持引用
        self.right_placeholder.lower()
        self.right_image_label.configure(image=photo)
        self.right_image_label.lift()
        self.save_btn.lift()

        # 恢复按钮状态
        self._set_buttons_state("normal")

    def save_image(self):
        if not self.processed_image_path:
            return
        import os
        from tkinter import filedialog

        # 生成默认文件名：原文件名_rmbg.png
        original_name = os.path.splitext(os.path.basename(self.processed_image_path))[0]
        default_filename = f"{original_name}.png"

        save_path = filedialog.asksaveasfilename(
            title="保存图片",
            initialfile=default_filename,
            defaultextension=".png",
            filetypes=[("PNG 图片", "*.png"), ("所有文件", "*")],
        )

        if save_path:
            try:
                img = Image.open(self.processed_image_path)
                img.save(save_path)
            except Exception as e:
                print(f"保存失败: {e}")

    def process_image(self):
        # 禁用所有按钮
        self._set_buttons_state("disabled")
        # 清空右边结果区域
        self.right_image_label.lower()
        self.right_image_label.configure(image="")
        self.save_btn.lower()
        self.processed_image_path = None  # 清空保存路径
        self.right_placeholder.configure(text="处理中...")
        self.right_placeholder.lift()
        self.root.update()

        # 3秒后执行实际处理（使用after避免阻塞UI）
        self.root.after(3000, self._do_process)


def main():
    root = ctk.CTk()
    app = ImageApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
