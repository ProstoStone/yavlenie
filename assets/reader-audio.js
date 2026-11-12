/* Optional text-to-speech reader: local browser voices, no external service. */
(() => {
  'use strict';
  document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('reader-listen-toggle');
    const panel = document.getElementById('reader-audio-panel');
    const prose = document.querySelector('.reading-page .prose');
    if (!toggle || !panel || !prose || !('speechSynthesis' in window) ||
        !('SpeechSynthesisUtterance' in window)) return;

    const synth = window.speechSynthesis;
    const lang = document.documentElement.lang === 'en' ? 'en-US' : 'ru-RU';
    const english = lang === 'en-US';
    const labels = english
      ? { ready: 'Ready to listen', playing: 'Reading', paused: 'Paused',
          done: 'Finished', stopped: 'Stopped', error: 'Voice playback is unavailable on this device',
          play: 'Play', restart: 'Restart', pause: 'Pause', resume: 'Resume' }
      : { ready: 'Готово к прослушиванию', playing: 'Чтение', paused: 'Пауза',
          done: 'Чтение завершено', stopped: 'Остановлено', error: 'Не удалось запустить голос на этом устройстве',
          play: 'Слушать', restart: 'Сначала', pause: 'Пауза', resume: 'Продолжить' };

    const play = document.getElementById('reader-audio-play');
    const pause = document.getElementById('reader-audio-pause');
    const stop = document.getElementById('reader-audio-stop');
    const rate = document.getElementById('reader-audio-rate');
    const voiceChoice = document.getElementById('reader-audio-voice');
    const section = document.getElementById('reader-audio-section');
    const status = document.getElementById('reader-audio-status');
    const key = 'yavlenie-audio-' + (english ? 'en' : 'ru');
    const saved = name => { try { return localStorage.getItem(key + '-' + name); } catch (_) { return null; } };
    const save = (name, value) => { try { localStorage.setItem(key + '-' + name, value); } catch (_) {} };

    // Assemble spoken chunks without duplicating nested paragraphs or reading the navigation.
    const chunks = [];
    const sections = [{ title: english ? 'From the beginning' : 'С начала текста', index: 0 }];
    function pushText(value) {
      const words = value.replace(/\s+/g, ' ').trim().split(' ').filter(Boolean);
      let part = '';
      for (const word of words) {
        if (part && part.length + word.length + 1 > 190) {
          chunks.push(part);
          part = '';
        }
        if (word.length > 190) {
          if (part) { chunks.push(part); part = ''; }
          for (let i = 0; i < word.length; i += 190) chunks.push(word.slice(i, i + 190));
        } else part = part ? part + ' ' + word : word;
      }
      if (part) chunks.push(part);
    }
    const heading = document.querySelector('.article-top h1');
    if (heading) pushText(heading.textContent);
    const deck = document.querySelector('.article-top .deck');
    if (deck) pushText(deck.textContent);
    prose.querySelectorAll('h2,h3,h4,p,li,figcaption,th,td').forEach(node => {
      if (node.parentElement && (node.parentElement.closest('li') || node.parentElement.closest('figcaption')))
        return;
      const value = node.textContent.replace(/\s+/g, ' ').trim();
      if (!value) return;
      if (/^H[234]$/.test(node.tagName)) {
        sections.push({ title: value, index: chunks.length });
      }
      pushText(value);
    });
    if (!chunks.length) return;

    sections.forEach(({ title, index }) => {
      const option = document.createElement('option');
      option.value = String(index);
      option.textContent = title;
      section.appendChild(option);
    });
    const storedRate = saved('rate');
    if ([...rate.options].some(option => option.value === storedRate)) rate.value = storedRate;

    let voices = [];
    function refreshVoices() {
      const previous = voiceChoice.value || saved('voice') || '';
      const all = synth.getVoices();
      const local = all.filter(v => v.lang.toLowerCase().startsWith(lang.slice(0, 2).toLowerCase()));
      voices = local.length ? local : all;
      voiceChoice.replaceChildren();
      const automatic = document.createElement('option');
      automatic.value = '';
      automatic.textContent = english ? 'Automatic' : 'Автоматически';
      voiceChoice.appendChild(automatic);
      voices.forEach(voice => {
        const option = document.createElement('option');
        option.value = voice.voiceURI;
        option.textContent = voice.name + ' (' + voice.lang + ')';
        voiceChoice.appendChild(option);
      });
      voiceChoice.value = voices.some(v => v.voiceURI === previous) ? previous : '';
    }
    refreshVoices();
    if (synth.addEventListener) synth.addEventListener('voiceschanged', refreshVoices);
    rate.addEventListener('change', () => save('rate', rate.value));
    voiceChoice.addEventListener('change', () => save('voice', voiceChoice.value));

    let serial = 0;
    let playing = false;
    let paused = false;
    let currentIndex = 0;
    let currentUtterance = null;

    function updateButtons() {
      play.textContent = playing ? (english ? 'Restart' : 'Сначала') : labels.play;
      pause.textContent = paused ? labels.resume : labels.pause;
      pause.disabled = !playing;
      stop.disabled = !playing;
      toggle.setAttribute('aria-pressed', String(playing));
    }
    function setStatus(value) { status.textContent = value; }
    function stopSpeech(message = labels.stopped) {
      serial++;
      playing = false;
      paused = false;
      currentUtterance = null;
      synth.cancel();
      currentIndex = Number(section.value || 0);
      setStatus(message);
      updateButtons();
    }
    function speakNext(token) {
      if (!playing || token !== serial) return;
      if (currentIndex >= chunks.length) {
        stopSpeech(labels.done);
        return;
      }
      const itemNumber = currentIndex + 1;
      const utterance = new SpeechSynthesisUtterance(chunks[currentIndex]);
      currentUtterance = utterance;
      utterance.lang = lang;
      utterance.rate = Number(rate.value) || 1;
      const chosen = voices.find(v => v.voiceURI === voiceChoice.value);
      if (chosen) utterance.voice = chosen;
      utterance.onstart = () => {
        if (token === serial) setStatus(labels.playing + ' · ' + itemNumber + ' / ' + chunks.length);
      };
      utterance.onend = () => {
        if (token !== serial) return;
        currentIndex++;
        currentUtterance = null;
        // The next short fragment is queued only after the previous one ends.
        speakNext(token);
      };
      utterance.onerror = e => {
        if (token !== serial || e.error === 'canceled' || e.error === 'interrupted') return;
        stopSpeech(labels.error);
      };
      try { synth.speak(utterance); }
      catch (_) { stopSpeech(labels.error); }
    }
    function begin() {
      if (playing) stopSpeech();
      else synth.cancel();
      serial++;
      playing = true;
      paused = false;
      currentIndex = Number(section.value || 0);
      updateButtons();
      speakNext(serial);
    }
    toggle.hidden = false;
    toggle.addEventListener('click', () => {
      panel.hidden = !panel.hidden;
      toggle.setAttribute('aria-expanded', String(!panel.hidden));
    });
    play.addEventListener('click', begin);
    pause.addEventListener('click', () => {
      if (!playing) return;
      if (paused) {
        synth.resume();
        paused = false;
        setStatus(labels.playing + ' · ' + (currentIndex + 1) + ' / ' + chunks.length);
      } else {
        synth.pause();
        paused = true;
        setStatus(labels.paused);
      }
      updateButtons();
    });
    stop.addEventListener('click', () => stopSpeech());
    section.addEventListener('change', () => {
      if (playing) stopSpeech(labels.ready);
      else currentIndex = Number(section.value || 0);
    });
    window.addEventListener('pagehide', () => {
      if (playing) stopSpeech();
    });
    setStatus(labels.ready);
    updateButtons();
  });
})();
