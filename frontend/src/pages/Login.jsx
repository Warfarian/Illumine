import Form from "../components/Forms";

function Login() {
    return (
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
            <Form route="/api/token/" method="login" />
        </div>
    );
}

export default Login;
