import './globals.css';

export const metadata = {
  title: 'LogLens',
  description: 'Production log explorer',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
