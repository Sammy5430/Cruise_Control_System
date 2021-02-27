//pin variables
const int led_pin = 13;
const int hall_pin = 3;
const int start_pin = 2;
//const int driver_en_pin = 4;
const int current_pin = 14;
const int voltage_pin = 15;
const int pwm_driver_pin = 9;
const int TEST_duty_pin = A2;

//system variables
int magnet_count = 0;
int duty = 0; //duty cycle 0=0%, 255=100%
float end_time = 0;
float start_time = 0;
float rpm=0;
float mph=0;
float v_sum = 0;
float i_sum = 0;
float v_avg = 0;
float i_avg = 0;
float num_samples = 0;
int val = 0;

int pwm = 0;
float diameter = 26; //inches
float set_value = 64.6; //5mph=64.6rpm set cruise control
bool cruise = false;
float cont = 0; //control equation voltage

void setup() 
{
  pinMode(hall_pin, INPUT);
  pinMode(start_pin, INPUT);
  pinMode(led_pin, OUTPUT);
  pinMode(current_pin, INPUT);
  pinMode(current_pin, INPUT);
  pinMode(pwm_driver_pin, OUTPUT);
//  pinMode(driver_en_pin, OUTPUT);
  pinMode(TEST_duty_pin, INPUT);
  
  attachInterrupt(digitalPinToInterrupt(hall_pin), hall_ISR, FALLING); //change, falling, rising
  attachInterrupt(digitalPinToInterrupt(start_pin), start_ISR, RISING);

  Serial.begin(9600);
//  digitalWrite(driver_en_pin, HIGH);
  
//  val = analogRead(TEST_duty_pin);
//  analogWrite(pwm_driver_pin, val/4); 
  
  start_time = millis();
}

void loop() 
{
//  Serial.print(analogRead(current_pin));
//  Serial.print("\n");
  if(!cruise)
  {
    val = analogRead(TEST_duty_pin);
    pwm = val/4;
  }
  analogWrite(pwm_driver_pin, pwm);
  /*
  v_sum = v_sum + ((analogRead(voltage_pin)*4.9)*5)/1000.0;
  i_sum = i_sum + (((analogRead(current_pin)-512)*4.9)/60.0) + 0.2; //0.2 offset
  num_samples += 1;
  delay(3);
  if(num_samples>=150)
  {
    v_avg = v_sum/num_samples;
    i_avg = i_sum/num_samples;
    Serial.print("\n");
    Serial.print(v_avg); //4.9mV/bit, based on 10-bit resolution
    Serial.print("V\n");
  
    Serial.print("\n");
    Serial.print(i_avg); //4.9mV/bit, based on 10-bit resolution
    Serial.print("A\n");
  
    num_samples = 0;
    v_sum = 0;
    i_sum = 0;
  }
  */
//  Serial.print("\n");
 
  if(magnet_count>=9)
  {
    end_time = millis();
    Serial.print("RPM: ");
    rpm = ((magnet_count * 60000)/(end_time-start_time))/9;
    mph = ((diameter/12)*3.14*rpm*60)/5280; 
    Serial.print(rpm, 2);
    Serial.print("\n");
    Serial.print("MPH: ");
    Serial.print(mph, 2);
    Serial.print("\n");
    magnet_count = 0;
    start_time = end_time;
    if(cruise == true) //if set, start cruise control
    {
      cont = (set_value - rpm)*(2); //gain = val/100 --- 2 is hardcoded gain example
      if(cont < 0)
      {
        cont = 0;
      }
      if(cont > 12)
      {
        cont = 12;
      }
       pwm = cont *(255/12); //ref-actual*gain*convert to pwm
//       Serial.print(pwm);
//       Serial.print("\n");
    }
  }
}

void hall_ISR()
{
  magnet_count+=1;
}

void start_ISR()
{
  cruise = !cruise;
}
