import processing.serial.*;

Serial myPort;  // Create object from Serial class
PFont f;
byte[] buf = new byte[18];
int[] data = new int[8];
int time = 0;
boolean vib_state = false;

void setup() 
{
	size(200, 200);
	String portName = "/dev/pts/18";
	myPort = new Serial(this, portName, 115200);
	
	f = createFont("Arial",16,true);
}

int conv(byte n1, byte n2)
{
	return ((n2 << 8) | (n1 & 0x00FF));
}

void draw()
{
	background(255);
	
	textFont(f,16);
	fill(0);
	text("Accel x :" + data[0],10,20);
	text("Accel y :" + data[1],10,40);
	text("Accel z :" + data[2],10,60);
	text("Touch  :" + data[3],10,80);
  // make the vibration motor "blink"
  if (millis() - time > 2000)
  {
    if (vib_state == false)
      myPort.write("1$");
    else
      myPort.write("0$");
    time = millis();
    vib_state = !vib_state;
  }
}

// serial event
void serialEvent(Serial p){
  p.readBytesUntil(42, buf);

  data[0] = conv(buf[0], buf[1]);
  data[1] = conv(buf[2], buf[3]);
  data[2] = conv(buf[4], buf[5]);
  data[3] = conv(buf[6], buf[7]);
}