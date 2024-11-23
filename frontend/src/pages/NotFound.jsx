import React from 'react';

function NotFound() {
    const containerStyle = {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: '#fffbf0',
        color: '#333',
        fontFamily: 'Comic Sans MS, cursive, sans-serif',
        textAlign: 'center',
        animation: 'fadeIn 1s ease-out',
    };

    const headingStyle = {
        fontSize: '56px',
        fontWeight: 'bold',
        color: '#ff6347',
        marginBottom: '20px',
        textShadow: '2px 2px 8px rgba(0, 0, 0, 0.1)',
    };

    const paragraphStyle = {
        fontSize: '20px',
        color: '#666',
        marginBottom: '30px',
        animation: 'bounce 1.5s infinite alternate',
    };

    const buttonStyle = {
        backgroundColor: '#ff6347',
        color: 'white',
        padding: '15px 30px',
        fontSize: '18px',
        fontWeight: 'bold',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer',
        marginTop: '20px',
        transition: 'all 0.3s ease',
    };

    const buttonHoverStyle = {
        backgroundColor: '#ff4500',
        transform: 'scale(1.1)',
    };

    const gifStyle = {
        width: '350px',
        maxWidth: '90%',
        marginTop: '20px',
        borderRadius: '10px',
        boxShadow: '0 8px 16px rgba(0, 0, 0, 0.2)',
        animation: 'shake 0.5s infinite alternate',
    };

    const goBack = () => {
        window.history.back();
    };

    return (
        <div style={containerStyle}>
            <h1 style={headingStyle}>404 Oops! Page Not Found</h1>
            <p style={paragraphStyle}>Looks like you've lost your way! 😅</p>
            <img
                src="https://media.giphy.com/media/l3vQXgToK3FrbAm2w/giphy.gif"
                alt="404 Error GIF"
                style={gifStyle}
            />
            <button
                style={buttonStyle}
                onMouseOver={(e) => e.target.style.backgroundColor = buttonHoverStyle.backgroundColor}
                onMouseOut={(e) => e.target.style.backgroundColor = buttonStyle.backgroundColor}
                onClick={goBack}
            >
                Go Back
            </button>
        </div>
    );
}

export default NotFound;
