// src/components/CurrentPrompt.js

import React, { useEffect, useState } from 'react';

function CurrentPrompt({ currentPrompt, nextRoundTime }) {
  const [countdown, setCountdown] = useState('N/A');

  useEffect(() => {
    let interval;

    const updateCountdown = () => {
      if (nextRoundTime) {
        const now = Date.now();
        const timeRemaining = Math.max(0, nextRoundTime - now);
        setCountdown(`${(timeRemaining / 1000).toFixed(1)} seconds`);

        if (timeRemaining <= 0) {
          setCountdown('Starting...');
        }
      } else {
        setCountdown('N/A');
      }
    };

    if (nextRoundTime) {
      interval = setInterval(updateCountdown, 100);
    } else {
      setCountdown('N/A');
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [nextRoundTime]);

  return (
    <div id="currentPrompt">
      <h3>Current Prompt: <span>{currentPrompt}</span></h3>
      <h3>Next Round Starts In: <span>{countdown}</span></h3>
    </div>
  );
}

export default CurrentPrompt;
