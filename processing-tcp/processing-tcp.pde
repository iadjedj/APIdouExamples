  
import processing.net.*;

int port = 3000;       
Server myServer;        
PFont f;

void setup()
{
  size(200, 200);
  background(0);
  myServer = new Server(this, port);
  
  f = createFont("Arial",16,true);
}

int[] accel = new int[3];
int[] gyro = new int[3];
int touch = 0;

void draw()
{
  background(255);
  
  textFont(f,16);
  fill(0);
  // Get the next available client
  Client thisClient = myServer.available();
  // If the client is not null, and says something, display what it said
  if (thisClient !=null) {
    String buff = thisClient.readString();
    buff = buff.replaceAll(";", "");
    String[] arr = split(buff, '\n');
    for (int i = 0; i < arr.length; i++)
    {
      int[] int_buff = int(split(arr[i], "\\ "));
      if (int_buff.length > 1)
      {
        if (int_buff[0] == 1 && int_buff.length == 4)
          arrayCopy(int_buff, 1, accel, 0, 3);
        else if (int_buff[0] == 2 && int_buff.length == 4)
          arrayCopy(int_buff, 1, gyro, 0, 3);
        else if (int_buff[0] == 3)
          touch = int_buff[1];
      }
    }
    text("Accel x :" + accel[0],10,20);
    text("Accel y :" + accel[1],10,40);
    text("Accel z :" + accel[2],10,60);
    text("Touch  :" + touch ,10,80);
  } 
}