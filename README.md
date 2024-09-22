# zerobug_pico
This project was inspired by [CoretechR](https://github.com/CoretechR) and its [ZeroBug-Lite](https://github.com/CoretechR/ZeroBug-Lite) project. 

It has agood CAD model, and is designed for small Raspberry Pi Zero.

In my opinion [Raspberry Pi Pico W](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#raspberry-pi-pico-and-pico-h) witch is much easier to use, especially for the beginners.<br>
There's also no need to setup SD-card, WiFi, create SSH connection etc.
All you need to start using PRi Pico W with [MicroPython](https://docs.micropython.org/en/latest/rp2/quickref.html) is just a USB cable and a lightweight  editor, e.g. [Thonny](https://thonny.org/).
# Project Structure

## _Software_ folder
Contains MCU and control device software

### _pico_ folder
Contains software for the Raspberry Pi Pico W
> [!NOTE]
> To run the software on the RPi Pico W microcontroller, 
> you need to install the MicroPython interpreter and copy the contents of the 'pico' folder to the microcontroller.

#### _servo_ folder
Contains drivers manage servos

#### _lcd_ folder
Contains driver for display information with LCD-display based on SSD1306 OLED 

#### _IMU_ folder
Contains driver for the inertial measurement units. MPU-6050 can measure acceleration, turn rate and the magnetic field in three axis.

## _Hardware_ folder
Contains schematic diagrams, PCB, BOM-files,

# Links
[MicroPython for Raspberry Pi RP2xxx boards](https://docs.micropython.org/en/latest/rp2/quickref.html)<br>
[Hexapod Leg Inverse Kinematics](https://www.youtube.com/watch?v=HjmIOKSp7v4)<br>
[Raspberry Pi to Pico Bluetooth](https://github.com/kevinmcaleer/pi_to_pico_bluetooth/tree/main) by [Kevin McAleer](https://github.com/kevinmcaleer)<br>
[PCA9685 for Pico](https://github.com/kevinmcaleer/pca9685_for_pico)
# CAD model
For CAD files, see the original project: https://github.com/CoretechR/ZeroBug

> [!IMPORTANT]
> 
> 
> <table>
>    <tr>
>        <td>gripper_clawl.stl</td>
>        <td>1pcs</td>
>    </tr>
>    <tr>
>        <td>gripper_body.stl</td>
>        <td>1pcs</td>
>    </tr>
>    <tr>
>        <td>tibia.stl</td>
>        <td>3pcs <b>+ 3pcs mirrored</b></td>
>    </tr>
>    <tr>
>        <td>body_top.stl</td>
>        <td>1pcs</td>
>    </tr>
>    <tr>
>        <td>body_bot.stl</td>
>        <td>1pcs</td>
>    </tr>
>    <tr>
>        <td>coxa.stl</td>
>        <td>3pcs <b>+ 3pcs mirrored</b></td>
>    </tr>
>    <tr>
>        <td>gripper_clawr.stl </td>
>        <td>1pcs</td>
>    </tr>
>    <tr>
>        <td>sock.stl</td>
>        <td>6pcs <b>mast be from elastic material</b></td>
>    </tr>
>    <tr>
>        <td>spacer.stl</td>
>        <td>1 pcs</td>
>    </tr>
>    <tr>
>        <td>femur.stl</td>
>        <td>6pcs</td>
>    </tr>
> </table>    
            