from abc import ABC, abstractmethod
import random


def otp_generator(length: int = 4) -> str:
    """
        Generate Random OTP
    """
    all_digits = list(map(str, range(10)))
    number = random.randint(length, length * 2)
    big_list = all_digits * number
    for _ in range(number):
        random.shuffle(big_list)
    return "".join(random.choices(big_list, k=length))


class OTP(ABC):
    """
        OTP Class
    """
    @abstractmethod
    def send_otp(self):
        """
            Send OTP
        """
        pass


class Mobile(object):
    """
        Mobile Number
    """

    def __init__(self, mobile: str):
        """
            Initilizer
        """
        self.mobile = mobile


class MCI(Mobile, OTP):
    """
        Hamrah-e-Aval
    """

    def send_otp(self, otp_length: int = 4):
        """
            Send OTP
        """
        otp = otp_generator(otp_length)
        # Choose Service Compatible with MCI
        return f"Code {otp} Has Benn Sent to {self.mobile} (MCI)", otp


class MTN(Mobile, OTP):
    """
        Irancell
    """

    def send_otp(self, otp_length: int = 4):
        """
            Send OTP
        """
        otp = otp_generator(otp_length)
        # Choose Service Compatible with MTN
        return f"Code {otp} Has Benn Sent to {self.mobile} (MTN)", otp


class OTPFactory(object):
    """
        Detect Mobile Number and Choose the Provider
    """
    MTN = ["093", "090"]
    MCI = ["091", "099"]

    def select_operator(self, mobile: str):
        """
            Select Operator based on Mobile Number
        """
        if mobile[:3] in self.MTN:
            return MTN(mobile)
        if mobile[:3] in self.MCI:
            return MCI(mobile)
        return None


def send_otp_client(mobile: str) -> str:
    """
        Shape Client Interface
    """
    otp_factory = OTPFactory()
    operator = otp_factory.select_operator(mobile)

    message, otp_code = "", ""

    if operator:
        message, otp_code = operator.send_otp()
        print(message)
        return message, otp_code

    print(
        f"Enter A Valid Mobile Number! {mobile} Is Not Valid Mobile Number."
    )
    return otp_code


if __name__ == "__main__":
    # print(otp_generator())
    # send_otp_client("09123456789")
    # send_otp_client("09301234567")
    pass
