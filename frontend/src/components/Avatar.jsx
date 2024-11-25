import '../styles/components/avatar.css';

function Avatar({ src, alt = "Profile", className = "", onUpload }) {
    const handleImageError = (e) => {
        e.target.src = 'https://w7.pngwing.com/pngs/205/731/png-transparent-default-avatar.png';
        e.target.onerror = null;
    };

    return (
        <div className="avatar-container">
            <img
                src={src || 'https://w7.pngwing.com/pngs/205/731/png-transparent-default-avatar.png'}
                alt={alt}
                className={`avatar-image ${className}`}
                onError={handleImageError}
            />
            {onUpload && (
                <label className="avatar-upload">
                    <input
                        type="file"
                        accept="image/*"
                        onChange={onUpload}
                    />
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M12 6v6m0 0v6m0-6h6m-6 0H6" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                </label>
            )}
        </div>
    );
}

export default Avatar;