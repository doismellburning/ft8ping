# ft8ping

ICMP over FT8.

Because [when FT8 Telemetry messages give you 71 bits of arbitrary content, why not do something ridiculous like stuff ICMP in there?](https://notes.doismellburning.co.uk/notebook/2025-05-06-understanding-the-ft8-binary-protocol/#telemetry-message-type).

## Usage

```
$ uv tool install --upgrade git+https://github.com/doismellburning/ft8ping
$ ft8ping send --source YOURCALL --destination THEIRCALL --radio-model 1 --radio-device /dev/radio --audio-device plughw:0,0
```
