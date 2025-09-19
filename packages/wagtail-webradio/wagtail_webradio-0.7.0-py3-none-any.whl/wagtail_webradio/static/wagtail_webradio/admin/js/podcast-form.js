/**
 * Format the time from seconds to HH:MM:SS.
 * @param {Number} seconds
 * @return {String}
 */
function formatDuration(seconds) {
  return new Date(1000 * seconds).toISOString().substr(11, 8);
}

class PodcastSoundController extends window.StimulusModule.Controller {
  static targets = ['duration', 'type', 'file', 'url'];
  static values = { type: String };

  connect() {
    if (this.hasTypeTarget) {
      this.typeValue = this.typeTarget.value;
    } else if (!this.hasFileTarget) {
      this.typeValue = 'url';
    }

    if (this.typeValue == 'url') {
      // Retrieve the current URL value and validate it
      const url = this.urlTarget.querySelector('input')?.value;

      if (url) {
        this.retrieve({ params: { url }});
      }
    }
  }

  typeValueChanged(type) {
    this.urlTarget.hidden = !(type === 'url');

    if (this.hasFileTarget) {
      this.fileTarget.hidden = !(type === 'file');
    }
  }

  setValid(isValid) {
    document.querySelector('input[name="is_sound_valid"]').value =
      isValid ? '1' : '0';
  }

  /**
   * Retrieve the duration of an audio file either defined by a `url`
   * parameter or by the value of the element that dispatched the event.
   */
  retrieve({ target, params }) {
    let url;

    this.setValid(false);

    if (params.url) {
      url = params.url;
    } else if (target) {
      url = target.files
        ? URL.createObjectURL(target.files[0])
        : target.value;
    }

    if (!url) {
      this.durationTarget.value = '';

      throw new Error(`Unable to get the sound URL from ${target}`);
    }

    const audio = new Audio();
    audio.preload = 'metadata';

    audio.addEventListener('error', () => {
      this.durationTarget.value = '';
    });
    audio.addEventListener('loadedmetadata', () => {
      this.durationTarget.value =
        audio.duration === Infinity ? '' : formatDuration(audio.duration);
      this.setValid(true);
    });

    audio.src = url;
  }

  /**
   * Set `type` value from the element that dispatched the event.
   */
  setType({ target }) {
    if (target) {
      this.typeValue = target.value;
    }
  }
}

window.wagtail.app.register('podcast-sound', PodcastSoundController);
