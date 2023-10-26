# Pedal Mapper

This is a simple program for mapping the buttons on an Elgato Stream Deck Pedal
to keyboard inputs. I use a pedal for push-to-talk when I play games with a
controller, and there wasn't anything that let me do that easily with the Elgato
Stream Deck Pedal.

## Dependencies

There aren't a lot of dependencies, but what you do need are:
- Python
- hidapi
- evdev

## How it works

The actual flow is really simple. You just configure three lists of key presses,
one for each button on the pedal, and then run the program. The program then
listens for button presses and sends the mapped keys to `/dev/uinput`.

Run the Python script and press your pedal. You can run it as a `systemd` unit
or equivalent to have it always running in the background.

You can find a list of all possible keycodes
[here](https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h).

## Possible issues

If you're using Wayland it won't work if your voice chat client isn't focused.
However, if you have a means of forwarding keystrokes to Xwayland applications
and your client is running in Xwayland, then it will work fine. KDE has this
built-in and that's what I use. There are other solutions like [this
script](https://github.com/Rush/wayland-push-to-talk-fix/) for forwarding
keystrokes.

There may be other issues. I haven't really run into any myself yet, but you
never know.

## Possible additions

This was just my first pass at implementing this specifically for my needs. The
code sucks, is basic as hell, and isn't very configurable. In no particular
order, things that I may implement in the future if I feel inspired are:
- Reading configuration from a file rather than being hardcoded into the
  program.
- Configuring other types of devices.
  [input-remapper](https://github.com/sezanzeb/input-remapper) is already a good
  general purpose solution, but it's possible there are unsupported devices for
  which people might want a similar solution to what is here.
- More advanced key combinations / macros. Right now the program just handles
  basic hold keys and press keys. Adding something like callbacks to associate
  with buttons could be neat, with a default one being how it works right now.
- Profiles/profile-switching would be neat. Being able to switch stuff on the
  fly would be handy if someone wanted to use different bindings for different
  situations.

These are all highly aspirational and I don't actually need any of these myself
currently. I'm lazy and selfish so it's actually unlikely I'll implement these,
but they're here as ideas in case anyone else wants to contribute.

## Contributing

Feel free to submit merge requests. I'm not too scary and would happily accept
contributions.