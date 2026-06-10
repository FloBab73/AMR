from camera_subscriber import NaoCameraCollector
from model import detect_and_segment

PROMPT = "Ein Tafelschwamm steht auf einer Oberfläche, suche den Tafelschwamm"
SIDEWAYS_MOTION_TOLERANCE = 0.1


def go_to_target_and_pick_up():
    camera = NaoCameraCollector()

    while True:
        image = camera.get_camera_data()
        object = detect_and_segment(image, PROMPT)
        # if not object:
        #     look_down()
        #     continue

        image_width = image.shape[1]
        target = object["mean"]["x"]
        if target > image_width * (0.5+SIDEWAYS_MOTION_TOLERANCE):
            shuffle_right()
        elif target < image_width * (0.5+SIDEWAYS_MOTION_TOLERANCE):
            shuffle_left()
        else:
            if foot_sensors_pressed():
                pickup_sponge()
            else:
                walk_straight()


def main():
    go_to_target_and_pick_up()


if __name__ == "__main__":
    main()
