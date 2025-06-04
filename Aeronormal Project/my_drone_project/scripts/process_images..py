import cv2
import os

def preprocess_image(img):
    
    img = cv2.resize(img, (800, 600))
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    equ = cv2.equalizeHist(gray)
    return equ

def stitch_images(image_folder):
    images = []

    if not os.path.exists(image_folder):
        print(f"Error: {image_folder} does not exist.")
        return None

    for filename in os.listdir(image_folder):
        img = cv2.imread(os.path.join(image_folder, filename))
        if img is not None:
            img = preprocess_image(img)
            images.append(img)
        else:
            print(f"Error: Could not read image {filename}")

    if len(images) < 2:
        print("Error: Need at least two images to stitch")
        return None

    stitcher = cv2.Stitcher_create()
    status, stitched = stitcher.stitch(images)

    if status == cv2.Stitcher_OK:
        return stitched
    else:
        print(f"Error during stitching: {status}")
        return None

if __name__ == "__main__":
    image_folder = os.path.join(os.path.dirname(__file__), "../data/images/")
    stitched_image = stitch_images(image_folder)
    if stitched_image is not None:
        output_file = os.path.join(os.path.dirname(__file__), "../data/stitched_image.jpg")
        cv2.imwrite(output_file, stitched_image)
        cv2.imshow("Stitched Image", stitched_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()