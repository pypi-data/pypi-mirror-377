import argparse
from datetime import date, timedelta

from datastation.managedeposit.manage_deposit import ManageDeposit
from datastation.common.config import init
from datastation.common.send_mail import SendMail


class ReportHandler:
    def __init__(self, server_url, cmd_args):
        self.__server_url = server_url
        self.__command_line_args = cmd_args

    def handle_request(self):
        report = ManageDeposit(self.__command_line_args).create_report(self.__server_url)

        if report is not None:
            output_file = self.__command_line_args.output_file
            if output_file == '-':
                print(report)
            else:
                if len(report.split('\n')) > 1:
                    self.save_report_to_file(report, output_file)

                    if self.__command_line_args.email_to is not None:
                        self.send_report_mail(output_file)
                else:
                    print("Report is empty.")

    def save_report_to_file(self, report, output_file):
        with open(output_file, 'w') as output:
            output.write(report)

    def send_report_mail(self, attachment):
        SendMail.send(self.__command_line_args.email_to,
                      "Deposits report ({})".format(self.__command_line_args.server.upper()),
                      "Please, find attached the detailed report of deposits.",
                      attachment,
                      self.__command_line_args.email_from_address,
                      self.__command_line_args.cc_email_to,
                      self.__command_line_args.bcc_email_to)


def main():
    config = init()
    parser = argparse.ArgumentParser(prog='deposit_create_report',
                                     description='Create and send reports based on dd-manage-deposit database')
    parser.add_argument('-o', '--output-file', dest='output_file', default='-',
                        help='the file to write the output and send recipient to a to or - for stdout')
    parser.add_argument('-e', '--enddate', dest='enddate', help='Filter until the record creation of this date')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-s', '--startdate', dest='startdate', help='Filter from the record creation of this date')
    group.add_argument('-a', '--age', dest='age', type=int, help='Filter from record creation not older than a number of days before today ')

    parser.add_argument('-t', '--state', help='The state of the deposit (repeatable)', action='append')
    parser.add_argument('-u', '--user', dest='user', help='The depositor name (repeatable)', action='append')
    parser.add_argument('-f', '--format', dest='file_format', default='text/csv', help='Output data format')
    parser.add_argument('-v', '--server', dest='server', default='unknown server', help='which server (prod/demo/..)')
    parser.add_argument('-r', '--from', dest='email_from_address', help='from address')
    parser.add_argument('--email-to', dest='email_to', help='when more than one recipient: comma separated emails')
    parser.add_argument('--cc-email-to', dest='cc_email_to', help='will be sent only if email-to is defined')
    parser.add_argument('--bcc-email-to', dest='bcc_email_to', help='will be sent only if email-to is defined')
    args = parser.parse_args()

    if args.age is not None: # Note: args is a Namespace object
        vars(args)['startdate'] = (date.today() + timedelta(days=-args.age)).strftime('%Y-%m-%d')

    server_url = config['manage_deposit']['service_baseurl'] + '/report'

    ReportHandler(server_url, args).handle_request()


if __name__ == '__main__':
    main()
