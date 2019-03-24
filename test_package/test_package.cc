#include <stdio.h>
#include <facedetectcnn.h>

int main()
{
	vector<FaceRect> f = objectdetect_cnn(NULL, 0, 0, 0);
	printf("Successfully initialized libfacedetection.\n");
	return 0;
}
