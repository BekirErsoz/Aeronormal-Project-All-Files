import cv2

def stitch_images(images):
    stitcher = cv2.createStitcher(cv2.Stitcher_PANORAMA)
    status, stitched = stitcher.stitch(images)
    if status == cv2.Stitcher_OK:
        return stitched
    else:
        print("Error during stitching")
        return None

images = [cv2.imread("image1.jpg"), cv2.imread("image2.jpg")]
stitched_image = stitch_images(images)
cv2.imwrite("stitched_image.jpg", stitched_image)