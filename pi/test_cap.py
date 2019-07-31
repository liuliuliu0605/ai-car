import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    print("Saving image.jpg...")
    cv2.imwrite('image.jpg', frame)
cap.release()
cv2.destroyAllWindows()
