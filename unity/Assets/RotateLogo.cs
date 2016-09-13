using UnityEngine;
using System.Collections;

public class RotateLogo : MonoBehaviour {

	// Use this for initialization
	void Start () {

	}

	// Update is called once per frame
	void Update () {
		float rotation_z = (APIdou.accel [0] / 16384.0f) * 90.0f;
		float rotation_x = (APIdou.accel [2] / 16384.0f) * 90.0f;

		transform.rotation = Quaternion.Euler(new Vector3 (rotation_x,0 , -rotation_z));

		if (APIdou.isTouched(APIdou.ANTENNA))
			Debug.Log ("Antenna Touched");
	}
}
