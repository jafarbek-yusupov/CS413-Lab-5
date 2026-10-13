// modified script with purpose to record battery voltage values
// given no viable option to do it with visual code
var __interpretation_started_timestamp__;
var pi = 3.141592653589793;

var d;
var p;
var pw;
var st;
var step;
var t;
var t0;
var theta_l;
var theta_r;
var battery;

var main = function()
{
	__interpretation_started_timestamp__ = Date.now();

	script.removeFile("log/motor_data_240057.txt");
	script.writeToFile("log/motor_data_240057.txt", "pwm,theta_l,theta_r,time,battery_v\n");

	p = 0;
	d = 1;
	step = 5;

	while (p <= 100) {
		pw = p * d;
		battery = brick.battery().readVoltage();

		brick.encoder(E3).reset();
		brick.encoder(E4).reset();

		st = "";
		t = 0;
		t0 = Date.now();

		brick.motor(M3).setPower(-pw);
		brick.motor(M4).setPower(pw);

		while (t < 2000) {
			theta_l = brick.encoder(E4).read();
			theta_r = brick.encoder(E3).read();
			t = Date.now() - t0;
			st = st + pw + "," + theta_l + "," + theta_r + "," + t + "," + battery + "\n";
			script.wait(5);
		}
		brick.motor(M3).powerOff();
		brick.motor(M4).powerOff();

		script.writeToFile("log/motor_data_240057.txt", st);

		script.wait(1000);

		d = -d;
		p = p + (step + step * d) / 2;
	}
	brick.playTone(1000, 300);
	script.wait(400);
	return;
}
