using UnityEngine;
using System.Collections;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.IO;
using System.Text;

public class APIdou : MonoBehaviour {

	static TcpListener listener;
	static bool is_open;
	static Thread t;
	public static int[] accel = new int[3];
	public static int[] gyro = new int[3];
	public static int touch = 0;
	public static int LEFT_FOOT		= 1;
	public static int RIGHT_FOOT	= 2;
	public static int LEFT_HAND		= 4;
	public static int RIGHT_HAND	= 8;
	public static int LEFT_EAR		= 16;
	public static int RIGHT_EAR		= 32;
	public static int ANTENNA		= 64;

	// Use this for initialization
	void Start () {
		listener = new TcpListener(IPAddress.Parse("127.0.0.1"), 3000);
		listener.Start();
		is_open = true;
		t = new Thread(new ThreadStart(Service));
		t.Start();
	}
	
	// Update is called once per frame
	void Update () {
	
	}

	void OnDestroy()
	{
		is_open = false;
		//t.Abort ();
	}

	static void convert(string[] array)
	{
		int[] tab = new int[4];

		for(int i = 0; i < array.Length; i++)
		{
			tab[i] = int.Parse(array[i]);
		}
		switch (tab [0])
		{
			case 1:
				System.Array.Copy (tab, 1, accel, 0, 3);
				break;
			case 2:
				System.Array.Copy (tab, 1, gyro, 0, 3);
				break;
			case 3:
				touch = tab [1];
				break;
		}
	}

	public static bool isTouched(int zones)
	{
		/*Returns True if the specified zone is touched.
		You can also use binary operation to check multiple zones at the same time
		*/
		if ((APIdou.touch & zones) != 0)
			return true;
		else
			return false;
		
	}

	public static void Service(){
		Debug.Log ("Waiting for the Python Script");
		// Todo : Find a way to close thread if it is here (blocking call)
		Socket soc = listener.AcceptSocket ();
		Debug.Log ("Socket found");
		while (is_open)
		{
			try {
				Stream s = new NetworkStream(soc); 
				StreamReader sr = new StreamReader(s);
				System.String str = sr.ReadLine();
				if (str != null)
				{
					// remove semicolon
					str = str.Remove(str.Length - 1);
					// split
					string[] arr = str.Split("\\".ToCharArray(), System.StringSplitOptions.RemoveEmptyEntries);
					convert(arr);
				//	print("Accel " + accel[0] + "/" + accel[1] + "/" + accel[2] +
				//		" / Gyro " + gyro[0] + "/" + gyro[1] + "/" + gyro[2] +
				//		"/ Touch " + touch); 
				}
			} catch (System.Exception e) {
				Debug.Log(e.Message);
			}
		}
		Debug.Log ("Thread Closed");
	}
}
