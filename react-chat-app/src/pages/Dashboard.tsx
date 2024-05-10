import React, { useState } from 'react';

const Login: React.FC = () => {
  const [username] = useState<string>('');

  return (
    <div>
      HomePage
      Welcome {username}
    </div>
  );
};

export default Login;