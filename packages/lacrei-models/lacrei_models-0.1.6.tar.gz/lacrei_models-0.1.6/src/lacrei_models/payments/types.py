from typing import TypedDict


class BankCodeData(TypedDict):
    code: str


class BankAccountData(TypedDict):
    bank: BankCodeData
    ownerName: str
    cpfCnpj: str
    agency: str
    account: str
    accountDigit: str
    bankAccountType: str


class CreditCard(TypedDict):
    holderName: str
    number: str
    expiryMonth: str
    expiryYear: str
    ccv: str


class CreditCardHolderInfo(TypedDict):
    name: str
    email: str
    cpfCnpj: str
    postalCode: str
    addressNumber: str
    phone: str
