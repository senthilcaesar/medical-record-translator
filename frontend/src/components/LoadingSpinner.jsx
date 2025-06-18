import React, { useEffect } from "react";
import { useSpring, animated, useSpringValue } from "@react-spring/web";

const LoadingSpinner = ({ message = "Processing...", progress = null }) => {
  // Animated progress value
  const progressValue = useSpringValue(0);

  // Update progress with spring animation
  useEffect(() => {
    if (progress !== null) {
      progressValue.start(progress);
    }
  }, [progress, progressValue]);

  // Spinning animation for the loader
  const spinnerAnimation = useSpring({
    from: { transform: "rotate(0deg)" },
    to: { transform: "rotate(360deg)" },
    config: { duration: 1000 },
    loop: true,
  });

  // Fade in animation for the component
  const fadeInAnimation = useSpring({
    from: { opacity: 0, transform: "translateY(20px)" },
    to: { opacity: 1, transform: "translateY(0px)" },
    config: { tension: 280, friction: 60 },
  });

  // Message animation with slight delay
  const messageAnimation = useSpring({
    from: { opacity: 0 },
    to: { opacity: 1 },
    delay: 200,
    config: { tension: 280, friction: 60 },
  });

  // Progress bar container animation
  const progressBarAnimation = useSpring({
    from: { opacity: 0, transform: "scale(0.9)" },
    to: { opacity: progress !== null ? 1 : 0, transform: "scale(1)" },
    config: { tension: 300, friction: 30 },
  });

  return (
    <animated.div
      style={fadeInAnimation}
      className="flex flex-col items-center justify-center p-8"
    >
      {/* Enhanced Spinner */}
      <div className="relative mb-6">
        {/* Background circle */}
        <div className="w-20 h-20 border-4 border-gray-200 rounded-full"></div>

        {/* Animated spinning circle */}
        <animated.div
          style={spinnerAnimation}
          className="absolute top-0 left-0 w-20 h-20 border-4 border-primary-600 rounded-full border-t-transparent"
        />

        {/* Inner pulsing dot */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <div className="w-3 h-3 bg-primary-600 rounded-full animate-pulse"></div>
        </div>
      </div>

      {/* Animated Message */}
      <animated.p
        style={messageAnimation}
        className="text-gray-700 font-medium text-lg mb-2 text-center"
      >
        {message}
      </animated.p>

      {/* Enhanced Progress Bar */}
      {progress !== null && progress >= 0 && (
        <animated.div style={progressBarAnimation} className="w-80 mt-6">
          {/* Progress Bar */}
          <div className="bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner">
            <animated.div
              className="bg-gradient-to-r from-primary-500 to-primary-600 h-full rounded-full shadow-sm"
              style={{
                width: progressValue.to((val) => `${val}%`),
                transition: "none", // Let React Spring handle the animation
              }}
            />
          </div>

          {/* Progress Text */}
          <div className="flex justify-between items-center mt-3">
            <span className="text-sm text-gray-500">Processing...</span>
            <animated.span className="text-sm font-semibold text-primary-600">
              {progressValue.to((val) => `${Math.round(val)}%`)}
            </animated.span>
          </div>

          {/* Progress Steps Indicator */}
          <div className="flex justify-between mt-4">
            <div className="flex items-center space-x-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  progress >= 25 ? "bg-primary-600" : "bg-gray-300"
                } transition-colors duration-300`}
              ></div>
              <span className="text-xs text-gray-500">Extract</span>
            </div>
            <div className="flex items-center space-x-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  progress >= 50 ? "bg-primary-600" : "bg-gray-300"
                } transition-colors duration-300`}
              ></div>
              <span className="text-xs text-gray-500">Identify</span>
            </div>
            <div className="flex items-center space-x-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  progress >= 75 ? "bg-primary-600" : "bg-gray-300"
                } transition-colors duration-300`}
              ></div>
              <span className="text-xs text-gray-500">Translate</span>
            </div>
            <div className="flex items-center space-x-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  progress >= 100 ? "bg-primary-600" : "bg-gray-300"
                } transition-colors duration-300`}
              ></div>
              <span className="text-xs text-gray-500">Complete</span>
            </div>
          </div>
        </animated.div>
      )}
    </animated.div>
  );
};

export default LoadingSpinner;
