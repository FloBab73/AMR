from camera_subscriber import NaoCameraCollector
from model import detect_and_segment

PROMPT = "Ein Tafelschwamm steht auf einer Oberfläche, suche den Tafelschwamm"


def go_to_target():
    camera = NaoCameraCollector()

    while True:
        image = camera.get_camera_data()
        object = detect_and_segment(image, PROMPT)
        if not object:
            look_down()
            continue

        image_width = image.shape[1]
        target = object["mean"]["x"]
        if target > image_width * 0.6:
            turn_right()
        elif target < image_width * 0.4:
            turn_left()
        else:
            walk_straight()



def main():
    go_to_target()


if __name__ == "__main__":
    main()
