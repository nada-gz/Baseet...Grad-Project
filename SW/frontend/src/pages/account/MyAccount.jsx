import useAuth from "../../hooks/useAuth";

export default function MyAccount() {
  const { user } = useAuth();

  return (
    <div>
      <h1>My Account</h1>
      <p>Email: {user?.email}</p>
      <p>Username: {user?.username}</p>
    </div>
  );
}
