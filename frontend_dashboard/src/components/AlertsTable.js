import SeverityBadge from "./SeverityBadge";

export default function AlertsTable({ alerts }) {
  return (
    <>
      <h3>⚠️ Alerts</h3>
      <table border="1" width="100%" cellPadding="8">
        <thead>
          <tr>
            <th>ID</th>
            <th>Message</th>
            <th>Severity</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map(alert => (
            <tr key={alert.id}>
              <td>{alert.id}</td>
              <td>{alert.message}</td>
              <td>
                <SeverityBadge level={alert.severity} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
