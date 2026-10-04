import dearpygui.dearpygui as dpg

dpg.create_context()

with dpg.font_registry():
    with dpg.font("C:/Windows/Fonts/DENG.ttf", 16) as font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
        dpg.bind_font(font)

def button_callback(sender, app_data, user_data):
    print(f"sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is: {user_data}")

def input_callback(sender, app_data, user_data):
	print(f"sender is: {sender}")
	print(f"app_data is: {app_data}")
	print(f"user_data is: {user_data}")
	s = dpg.get_value(sender)
	print(s)
	try:
		dpg.set_value("Slider Float", float(s))
	except ValueError:
		print("输入值不是数字")

def change_text(sender, app_data, user_data):
	print(f"sender is: {sender}")
	print(f"app_data is: {app_data}")
	print(f"user_data is: {user_data}")
	dpg.set_value("text item", f"Mouse Button ID: {app_data}")

with dpg.window(tag="Main Window"):
	with dpg.item_handler_registry(tag="widget handler") as handler:
		dpg.add_item_clicked_handler(callback=change_text)

	with dpg.group(horizontal=True):
		with dpg.child_window(tag="Control Panel", width=300):
			dpg.add_text("Developer: SteveZhang08", tag="eggs")
			dpg.bind_item_handler_registry("eggs", "widget handler")
			b = dpg.add_button(tag="Save Button", label="Save", callback=button_callback)
			dpg.add_input_text(label="string", default_value="在此处设置下面滑动条的值", callback=input_callback)
			dpg.add_slider_float(tag="Slider Float", label="float", default_value=0.273, max_value=1)
			dpg.add_text("控制面板")
			dpg.add_separator()
			dpg.add_button(tag="Add Cell Button", label="添加细胞")
			dpg.add_button(tag="Add Resource Button", label="添加资源")

		with dpg.child_window(width=-1, height=-1, tag="canvas_container", no_scrollbar=True):
        	# 创建绘图画布
			dpg.add_drawlist(width=800, height=600, tag="simulation_canvas")
			def call_ces(sender, app_data, user_data):
				print(f"sender is: {sender}")
				print(f"app_data is: {app_data}")
				print(f"user_data is: {user_data}")
			def draw_cell(x, y):
				with dpg.draw_node(parent="simulation_canvas"):
					cell = dpg.draw_circle((x, y), radius=10.0,color=(255, 0, 0), tag="Cell")
					dpg.draw_rectangle(
                		pmin=(0, 0),
                		pmax=(800, 600),
                		color=(20, 20, 25, 255),
                		fill=(20, 20, 25, 255)
            		)
			draw_cell(100, 100)

print(b)

dpg.create_viewport(title='VitaeCanvas GUI', width=600, height=200)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Main Window", True)	# 设置主窗口为"Main Window"窗口
# dpg.start_dearpygui()
while dpg.is_dearpygui_running():
	dpg.render_dearpygui_frame()

dpg.destroy_context()