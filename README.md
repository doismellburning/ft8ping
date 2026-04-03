# ft8ping

ICMP over FT8.

Because [when FT8 Telemetry messages give you 71 bits of arbitrary content, why not do something ridiculous like stuff ICMP in there?](https://notes.doismellburning.co.uk/notebook/2025-05-06-understanding-the-ft8-binary-protocol/#telemetry-message-type).

## Usage

```
$ uv tool install --upgrade git+https://github.com/doismellburning/ft8ping
$ ft8ping send --source YOURCALL --destination THEIRCALL --radio-model 1 --radio-device /dev/radio --audio-device plughw:0,0
```

## Status

I got as far as encoding a ping in an FT8 message,
then got side-tracked by the amount of wrangling involved to not only respond but also to acknowledge the responses.
For example, not only would the receiver need to be a daemon hooked up to WSJT-X or something similar to handle the decoding
(I don't want to do the DSP myself)
but the sender would need something equivalent to acknowledge the replies.

So right now this doesn't do much more than send Telemetry messages that will likely confuse other people.
But I enjoyed digging into FT8's binary protocol along the way.
