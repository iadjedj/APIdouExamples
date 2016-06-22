import processing.serial.*;

Serial myPort;  // Create object from Serial class
PFont f;

void setup() 
{
	size(200, 200);
	String portName = "/dev/pts/17";
	myPort = new Serial(this, portName, 115200);
	
	// Dirty way to flush serial and sync it to python
	int tmp = myPort.read();
	myPort.readBytes(tmp % 8);
	
	f = createFont("Arial",16,true);
}

int conv(byte n1, byte n2)
{
	return ((n2 << 8) | (n1 & 0x00FF));
}

void draw()
{
	background(255);
	if (myPort.available() >= 8)
	{
		byte[] buf = new byte[8];
		int[] data = new int[4];
		
		myPort.readBytes(buf);
		data[0] = conv(buf[0], buf[1]);
		data[1] = conv(buf[2], buf[3]);
		data[2] = conv(buf[4], buf[5]);
		data[3] = conv(buf[6], buf[7]);
		
		textFont(f,16);
		fill(0);
		text("Accel x :" + data[0],10,20);
		text("Accel y :" + data[1],10,40);
		text("Accel z :" + data[2],10,60);
		text("Touch  :" + data[3],10,80);
	}
}
