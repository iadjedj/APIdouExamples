import processing.serial.*;
import processing.opengl.*;
Serial myPort;

PFont font;
int[] xAxis;
int[] yAxis;
int[] zAxis;

int currentX = 0;
int currentY = 0;
int currentZ = 0;
int touch = 0;
int oneGSensorValue = 16384;

int totalReadings = 400;
int readingPos = 0; // the reading position in the array

void setup()
{
	hint(DISABLE_OPTIMIZED_STROKE);
	smooth();
	size(600, 300, OPENGL); 

	font = createFont("Arial", 24);
	textFont(font, 24);

	xAxis = new int[totalReadings];
	yAxis = new int[totalReadings];
	zAxis = new int[totalReadings];

	myPort = new Serial(this, "/dev/pts/7", 115200);
	// Dirty way to flush serial and sync it to python
	int tmp = myPort.read();
	myPort.readBytes(tmp % 8);
	noLoop();
}

void draw()
{
	background(#BBBBBB);
	drawGraph(xAxis, 100, color(#519050), "X - Axis");  
	drawGraph(yAxis, 200, color(#708CDE), "Y - Axis");
	drawGraph(zAxis, 300, color(#D38031), "Z - Axis");
	text("Touch :" + touch, 450, 190);
 // draw3d(currentX, currentY, currentZ);
}

int conv(byte n1, byte n2)
{
	return ((n2 << 8) | (n1 & 0x00FF));
}

void serialEvent(Serial p)
{
	try
	{
		if (p.available() >= 8)
		{
			byte[] buf = new byte[8];
			p.readBytes(buf);
			currentX = conv(buf[0], buf[1]);
			currentY = conv(buf[2], buf[3]);
			currentZ = conv(buf[4], buf[5]);
			touch = conv(buf[6], buf[7]);
			xAxis = insertValueIntoArray(xAxis, currentX, readingPos, totalReadings);
			yAxis = insertValueIntoArray(yAxis, currentY, readingPos, totalReadings);
			zAxis = insertValueIntoArray(zAxis, currentZ, readingPos, totalReadings);
			readingPos = readingPos + 1; // increment the array position
		}
	}
	catch(Exception e)
	{
	 println(e);
	}
	redraw();
}


void drawGraph(int[] arrToDraw, int yPos, color graphColor, String name){
	int arrLength = arrToDraw.length;
	stroke(graphColor);
	for (int x=0; x<arrLength - 1; x++)
	{
		float normalizedLine = norm(arrToDraw[x], -16384.0f, 16384.0f);
		float lineHeight = map(normalizedLine, 0, 1, 0.00, 85.0);
		line(x, yPos, x, yPos - int(lineHeight));
	}
	
	pushStyle();
	stroke(#FFFFFF);
	fill(#FFFFFF);
	String gString = nfc(gFromSensorValue(arrToDraw[arrLength - 2]), 2);
	text(name + " : " + gString + " Gs", 10, yPos - 10);
	popStyle();
}

void draw3d(int currentX, int currentY, int currentZ){
	float finalX = currentX / 16384.0f;
	float finalY = currentY / 16384.0f;
	float finalZ = currentZ / 16384.0f;

	pushMatrix();
	ambientLight(102, 102, 102);
	lightSpecular(204, 204, 204);
	directionalLight(102, 102, 102, -1, -1, -1);
	shininess(1.0);
	translate(500, 250);
	rotateY(finalZ);
	rotateX(-finalX);
	fill(#E2E8D5);
	noStroke();
	fill(#B76F6F);
	float heightWidth = finalX * 1.8;
	box(65, 65, 50);
	popMatrix();
}

int[] insertValueIntoArray(int[] targetArray, int val, int pos, int maxLength)
{
	if(pos > (maxLength-1))
	{
		// if the pos == maxSize, shift the array to retain the original value
		int[] returnArray = subset(targetArray, 1, maxLength-1);
		returnArray = expand(returnArray, maxLength);
		returnArray[maxLength-2] = val;
		return returnArray;
	}
	else
	{
		targetArray[pos] = val;
		return targetArray;
	}
}

float gFromSensorValue(int sensorValue){
	return sensorValue/16384.0f;
}

void smallFont() {	 }
void mediumFont(){	textFont(font, 30); }
void largeFont() {	textFont(font, 40); }